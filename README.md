# Radarr Config
"Radarr Config" is a python SideCar container to configure an radarr instance.

This SideCar container is usable to configure :
- Radarr settings (Root Folders, Remote Path Mappings and "Forms" authentication)
- Jackett indexer
- Transmission donwloader

## How to deploy Radarr with Radar Config
### Initialize your environment
Before deploy your Radarr instance with Radarr config, you have to generate **ConfigMap** and **Secret** :
- Radarr settings :
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: radarr-config
data:
  RADARR_ROOTPATH: *********
  RADARR_REMOTEPATH: *********
  RADARR_LOCALPATH: *********
```
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: radarr-secret
data:
  RADARR_USER: *********
  RADARR_PASSWORD: *********
type: Opaque
```

- Jackett indexer :
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: jackett-config
data:
  INDEXER_NAME: *********
  INDEXER_URL: *********
  INDEXER_APIKEY: *********
```

- Transmission downloader :
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: transmission-config
data:
  DOWNLOAD_NAME: *********
  DOWNLOAD_URL: *********
  DOWNLOAD_PORT: *********
  DOWNLOAD_FILMCATEGORY: *********
```
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: transmission-secret
data:
  DOWNLOAD_USER: *********
  DOWNLOAD_PASSWORD: *********
type: Opaque
```

### Deploy Radarr
```yaml
      containers:
        - image: lscr.io/linuxserver/radarr:latest
          name: radarr
          volumeMounts:
            - name: radarr-config
              mountPath: /config
            - name: media-data
              subPath: downloads
              mountPath: /downloads
            - name: media-data
              mountPath: /movies
        - image: quay.io/bizalu/radarr-config:latest
          name: radarr-config
          envFrom:
            - configMapRef:
                name: radarr-config
            - secretRef:
                name: radarr-secret
            - configMapRef:
                name: jackett-config
            - configMapRef:
                name: transmission-config
            - secretRef:
                name: transmission-secret
          volumeMounts:
            - name: radarr-config
              mountPath: /config
```
