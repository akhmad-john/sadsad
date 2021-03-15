from smi.zone.models import Zone, ZoneFile
from smi.factory.models import Factory
import pandas as pd


def parse_zone_from_file(obj_id):
    obj = ZoneFile.objects.get(id=obj_id)
    df = pd.read_excel(obj.file.file)
    df.replace({pd.np.nan: None}, inplace=True)
    error_list = zones_list_to_models(df.values.tolist())
    if error_list:
        ZoneFile.objects.filter(id=obj.id).update(errors=error_list)
    return error_list


def zones_list_to_models(values_list):
    error_list = []
    for i, row in enumerate(values_list):
        try:
            factory = Factory.objects.get(plant_id=row[0])
            Zone.objects.update_or_create(
                factory=factory,
                zone_id=row[1],
                zonename=row[2],
                head_panel=row[4],
                p_number=row[5],
                p_name=row[6],
                ip_address=row[7],
                indicator=row[3],
                direction=row[7]
            )
        except Exception as e:
            error_list.append({i+2: row, "Error": f'{e}'})
    return error_list
