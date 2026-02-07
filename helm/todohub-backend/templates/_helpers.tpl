{{/*
Common labels
*/}}
{{- define "todohub-backend.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: todohub
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todohub-backend.selectorLabels" -}}
app: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Full name
*/}}
{{- define "todohub-backend.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}
