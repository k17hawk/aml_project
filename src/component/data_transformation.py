from src.entity.schema import TransactionDataSchema
from pyspark.ml.feature import StandardScaler, VectorAssembler, StringIndexer
from pyspark.ml.pipeline import Pipeline
from src.config.spark_manager import spark_session
from src.exception import AMLException
from src.logger import  logging as logger
from src.entity.artifcat_entity import DataValidationArtifact, DataTransformationArtifact
from src.entity.config_entity import DataTransformationConfig
from pyspark.sql import DataFrame
from src.ml.features import DateTimeFeatureExtractor,DropColumnsTransformer,TypeCastingTransformer
from pyspark.sql.functions import col, rand
import os,sys
from functools import reduce
from data_access.data_transformation_artifact import DataTransformationArtifactData
class DataTransformation:

    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig,
                 schema=TransactionDataSchema()
                 ):
        try:
            logger.info(f"{'>>' * 20}Starting data transformation.{'<<' * 20}")
            self.data_transformation_data = DataTransformationArtifactData()
            self.data_val_artifact = data_validation_artifact
            self.data_tf_config = data_transformation_config
            self.schema = schema
        except Exception as e:
            raise AMLException(e, sys)

    def read_data(self) -> DataFrame:
        try:
            file_path = self.data_val_artifact.accepted_file_path
            dataframe: DataFrame = spark_session.read.parquet(file_path)
            dataframe.printSchema()
            return dataframe
        except Exception as e:
            raise AMLException(e, sys)
    
    def get_data_transformation_pipeline(self, ) -> Pipeline:
        try:   
            stages = []
            #generating date & time variant
            logger.info("applying derived feature Transformer")
            derived_feature = DateTimeFeatureExtractor(inputCols=self.schema.derived_input_features,
                                                      outputCols=self.schema.derived_output_features)  
            stages.append(derived_feature)
            #dropping date and time
            logger.info("applying Drop column transfomer")
            drop_cols_transformer = DropColumnsTransformer(input_cols=self.schema.unwanted_columns)
            
            stages.append(drop_cols_transformer)


            logger.info("Applying String indxer Transformer")
            #string index 
            for string_input,string_output in zip(self.schema.string_indexing_input_features,
                                                  self.schema.string_indexing_out_features):
                string_indexer = StringIndexer(inputCol=string_input,outputCol=string_output)

                stages.append(string_indexer)
            logger.info("converting data types")
            type_cast_transformer = TypeCastingTransformer(inputCols=self.schema.numerical_columns + [self.schema.target_column], 
                                      outputCols=self.schema.numerical_out_columns + [self.schema.target_column])
            
            stages.append(type_cast_transformer)
            logger.info("Applying vector assameber Transformer")
            
            assembled_col = [col for col in self.schema.numerical_out_columns if col!=self.schema.target_column]
            vector_assambler = VectorAssembler(inputCols=assembled_col,
                                               outputCol=self.schema.vector_assembler_out_cols)
            stages.append(vector_assambler)
            logger.info("applying standard scaler")
            # print(self.schema.vector_assembler_out_cols)
            standard_scaler = StandardScaler(inputCol=self.schema.vector_assembler_out_cols,
                                             outputCol=self.schema.scaled_vector_input_features)
            stages.append(standard_scaler)
            pipeline = Pipeline(
                stages=stages
            )
            logger.info(f"Data transformation pipeline completed: [{pipeline}]")
            return pipeline
        except Exception as e:
            raise AMLException(e, sys)
    
    

    def get_balanced_shuffled_dataframe(self, dataframe: DataFrame) -> DataFrame:
        try:
            count_of_each_cat = dataframe.groupby(self.schema.target_column).count().collect()
            
            label = []
            n_record = []
            for info in count_of_each_cat:
                n_record.append(info['count'])
                label.append(info[self.schema.target_column])
            # Finding  the majority class count
            majority_row = max(n_record)  
            # Oversampling fraction
            n_per = [majority_row / record for record in n_record]  

            selected_row = []
            for label, per in zip(label, n_per):
                print(label, per)
                temp_df = dataframe.filter(col(self.schema.target_column) == label)
                
                # Performing Oversampling
                if per > 1:
                    temp_df = temp_df.sample(withReplacement=True, fraction=per, seed=42)
                
                selected_row.append(temp_df)

            selected_df: DataFrame = selected_row[0]
            for df in selected_row[1:]:
                selected_df = selected_df.union(df)

            # Shuffling the data
            selected_df = selected_df.orderBy(rand())  
            selected_df.groupby(self.schema.target_column).count().show()

            return selected_df
        except Exception as e:
            raise AMLException(e, sys)

        
    
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logger.info(f">>>>>>>>>>>Started data transformation <<<<<<<<<<<<<<<")
            dataframe: DataFrame = self.read_data()
            dataframe = self.get_balanced_shuffled_dataframe(dataframe=dataframe)
            logger.info(f"Number of row: [{dataframe.count()}] and column: [{len(dataframe.columns)}]")

            test_size = self.data_tf_config.test_size
            logger.info(f"Splitting dataset into train and test set using ration: {1 - test_size}:{test_size}")
            train_dataframe, test_dataframe = dataframe.randomSplit([1 - test_size, test_size])
            logger.info(f"Train dataset has number of row: [{train_dataframe.count()}] and"
                        f" column: [{len(train_dataframe.columns)}]")

            logger.info(f"Test dataset has number of row: [{test_dataframe.count()}] and"
                        f" column: [{len(test_dataframe.columns)}]")
            
            pipeline = self.get_data_transformation_pipeline()
            transformed_pipeline = pipeline.fit(train_dataframe)

            required_columns = [self.schema.scaled_vector_input_features, self.schema.target_column]

            transformed_trained_dataframe = transformed_pipeline.transform(train_dataframe)
            print(transformed_trained_dataframe.printSchema())
            any_null = reduce(lambda a, b: a | b, (col(c).isNull() for c in transformed_trained_dataframe.columns))

            has_null = transformed_trained_dataframe.filter(any_null).count() > 0

            print(f"DataFrame has nulls: {has_null}")

            # print(transformed_trained_dataframe.show(10))
            transformed_trained_dataframe = transformed_trained_dataframe.select(required_columns)  

            transformed_test_dataframe = transformed_pipeline.transform(test_dataframe)
            transformed_test_dataframe = transformed_test_dataframe.select(required_columns)


            export_pipeline_file_path = self.data_tf_config.export_pipeline_dir

            # creating required directory
            os.makedirs(export_pipeline_file_path, exist_ok=True)
            os.makedirs(self.data_tf_config.transformed_test_dir, exist_ok=True)
            os.makedirs(self.data_tf_config.transformed_train_dir, exist_ok=True)
            transformed_train_data_file_path = os.path.join(self.data_tf_config.transformed_train_dir,
                                                            self.data_tf_config.file_name
                                                            )
            transformed_test_data_file_path = os.path.join(self.data_tf_config.transformed_test_dir,
                                                           self.data_tf_config.file_name
                                                           )

            logger.info(f"Saving transformation pipeline at: [{export_pipeline_file_path}]")
            # print(export_pipeline_file_path)
            # print(type(transformed_pipeline))
            # transformed_pipeline.save(r"C:\Users\lang-chain\Documents\aml_project\testing")
            transformed_pipeline.save(export_pipeline_file_path)
            logger.info(f"Saving transformed train data at: [{transformed_train_data_file_path}]")
            print(transformed_trained_dataframe.count(), len(transformed_trained_dataframe.columns))
            transformed_trained_dataframe.write.parquet(transformed_train_data_file_path)

            logger.info(f"Saving transformed test data at: [{transformed_test_data_file_path}]")
            print(transformed_test_dataframe.count(), len(transformed_trained_dataframe.columns))
            transformed_test_dataframe.write.parquet(transformed_test_data_file_path)

            data_tf_artifact = DataTransformationArtifact(
                transformed_train_file_path=transformed_train_data_file_path,
                transformed_test_file_path=transformed_test_data_file_path,
                exported_pipeline_file_path=export_pipeline_file_path,

            )

            self.data_transformation_data.save_transformation_artifact(data_transformation_artifact=data_tf_artifact)
            logger.info(f"{'>>' * 20} Data Transformation completed.{'<<' * 20}")
            return data_tf_artifact
            
            
        except Exception as e:
            raise AMLException(e,sys)