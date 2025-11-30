import Trainer
import os

SQL_COLUMNS = "select distinct mac_bssid from tfm_ips.referencepointswifi order by mac_bssid asc;"

SQL_TRAINING = """select CONCAT(originalfileid,'_',posiapptimestamp) id,originalfileid,posiapptimestamp,mac_bssid,rss,floorid 
from tfm_ips.ReferencePointsPositionWifi posi_wifi
join tfm_ips.originalfile ON originalfile.id = posi_wifi.originalfileid
where originalfile.filename like '%TrainingTrial%'
order by id, mac_bssid asc"""

SQL_TESTING = """select CONCAT(originalfileid,'_',posiapptimestamp) id,originalfileid,posiapptimestamp,mac_bssid,rss,floorid
from tfm_ips.ReferencePointsPositionWifi posi_wifi
join tfm_ips.originalfile ON originalfile.id = posi_wifi.originalfileid
where originalfile.filename like '%ScoringTrial%'
order by id, mac_bssid asc"""

Trainer.logging_info(f"TRAINING: {os.path.basename(__file__)}")
Trainer.train_floor_detection_model(SQL_COLUMNS, SQL_TRAINING, SQL_TESTING)
