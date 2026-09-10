[1mdiff --git a/vercel-frontend/vercel.json b/vercel-frontend/vercel.json[m
[1mindex 34ceb567..eb9e8478 100644[m
[1m--- a/vercel-frontend/vercel.json[m
[1m+++ b/vercel-frontend/vercel.json[m
[36m@@ -1,13 +1,13 @@[m
 {[m
   "outputDirectory": "vercel-frontend",[m
   "rewrites": [[m
[31m-    { "source": "/health",           "destination": "http://3.0.103.1:8000/health" },[m
[31m-    { "source": "/extract-facts",    "destination": "http://3.0.103.1:8000/extract-facts" },[m
[31m-    { "source": "/predict-severity", "destination": "http://3.0.103.1:8000/predict-severity" },[m
[31m-    { "source": "/map-riddor",       "destination": "http://3.0.103.1:8000/map-riddor" },[m
[31m-    { "source": "/analyse-causes",   "destination": "http://3.0.103.1:8000/analyse-causes" },[m
[31m-    { "source": "/analyse-causes-amended", "destination": "http://3.0.103.1:8000/analyse-causes-amended" },[m
[31m-    { "source": "/find-patterns",    "destination": "http://3.0.103.1:8000/find-patterns" },[m
[31m-    { "source": "/triage",           "destination": "http://3.0.103.1:8000/triage" }[m
[32m+[m[32m    { "source": "/health",           "destination": "http://13.212.129.12:8000/health" },[m
[32m+[m[32m    { "source": "/extract-facts",    "destination": "http://13.212.129.12:8000/extract-facts" },[m
[32m+[m[32m    { "source": "/predict-severity", "destination": "http://13.212.129.12:8000/predict-severity" },[m
[32m+[m[32m    { "source": "/map-riddor",       "destination": "http://13.212.129.12:8000/map-riddor" },[m
[32m+[m[32m    { "source": "/analyse-causes",   "destination": "http://13.212.129.12:8000/analyse-causes" },[m
[32m+[m[32m    { "source": "/analyse-causes-amended", "destination": "http://13.212.129.12:8000/analyse-causes-amended" },[m
[32m+[m[32m    { "source": "/find-patterns",    "destination": "http://13.212.129.12:8000/find-patterns" },[m
[32m+[m[32m    { "source": "/triage",           "destination": "http://13.212.129.12:8000/triage" }[m
   ][m
 }[m
\ No newline at end of file[m
