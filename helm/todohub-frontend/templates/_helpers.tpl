{{/*
Common labels
*/}}
{{- define "todohub-frontend.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: todohub
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todohub-frontend.selectorLabels" -}}
app: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Full name
*/}}
{{- define "todohub-frontend.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}
