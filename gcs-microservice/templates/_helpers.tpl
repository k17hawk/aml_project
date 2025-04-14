{{- define "gcs-microservice.fullname" -}}
{{ .Release.Name }}-gcs-to-kafka
{{- end }}

{{- define "gcs-microservice.labels" -}}
app: {{ include "gcs-microservice.fullname" . }}
chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
release: "{{ .Release.Name }}"
heritage: "{{ .Release.Service }}"
{{- end }}