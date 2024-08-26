import os
import json
import dotenv
import pandas as pd

class JsonConverter:

    SOCIOS = 'socios'
    ESTABELECIMENTO = 'estabelecimento'
    ATIVIDADES_SECUNDARIAS = 'atividades_secundarias'
    CNPJ = 'cnpj'

    def __init__(self):
        dotenv.load_dotenv()
        self.subfolder = os.getenv("SUBFOLDER_PATH")
        self.generalFileName = os.getenv("GENERAL_CNPJ_FILE_NAME")
        self.socioFileName = os.getenv("SOCIOS_FILE_NAME")
        self.atividadesSecundariasFileName = os.getenv("ATIVIDADES_SECUNDARIAS_FILE_NAME")

        self.dfList = []
        self.sociosList = []
        self.atividadesSecundariasList = []

        self.df = self.setGeneralDF()
        self.socios = self.setSociosDF()
        self.atividadesSecundarias = self.setAtividadesSecundariasDF()
    
    def readJSONSubfolder(self):
        
        for jsons in os.listdir(self.subfolder):
            with open(os.path.join(self.subfolder, jsons)) as jsonFile:
                data = json.load(jsonFile)

                self.processNesteData(data, self.SOCIOS)
                self.processNesteData(data, self.ESTABELECIMENTO)

            df = pd.json_normalize(data)

            self.dfList.append(df)

    def processNesteData(self, data, field):
        if field == self.SOCIOS in data and data[self.SOCIOS]:
            socios = data[self.SOCIOS]
            for socio in socios:
                socio[self.CNPJ] = data.get('estabelecimento', {}).get('cnpj', None)
                self.sociosList.append(socio)
        elif field == self.ESTABELECIMENTO in data and self.ATIVIDADES_SECUNDARIAS in data[self.ESTABELECIMENTO]:
            atividadesSecundarias = data[self.ESTABELECIMENTO][self.ATIVIDADES_SECUNDARIAS]
            for atividadeSecundaria in atividadesSecundarias:
                atividadeSecundaria[self.CNPJ] = data.get(self.ESTABELECIMENTO, {}).get(self.CNPJ, None)
                self.atividadesSecundariasList.append(atividadeSecundaria)
            
    def setGeneralDF(self):

        self.readJSONSubfolder()

        superDF = pd.concat(self.dfList, ignore_index=True)
        superDF = superDF.fillna('')

        return superDF
    
    def setSociosDF(self):
        return pd.DataFrame(self.sociosList)
    
    def setAtividadesSecundariasDF(self):
        return pd.DataFrame(self.atividadesSecundariasList)
    
    def dfToExcel(self):
        self.df.to_excel(self.generalFileName, index=False)

    def sociosDfToExcel(self):
        self.socios.to_excel(self.socioFileName, index=False)

    def atividadesSecundariasToExcel(self):
        self.atividadesSecundarias.to_excel(self.atividadesSecundariasFileName, index=False)

    def saveExcel(self):
        self.dfToExcel()
        self.sociosDfToExcel()
        self.atividadesSecundariasToExcel()

teste = JsonConverter()
teste.saveExcel()
print(teste.socios)

"""
if 'socios' in data and data['socios']:
    socios = data['socios']
    for socio in socios:
        socio['cnpj'] = data.get('estabelecimento', {}).get('cnpj', None)
        self.sociosList.append(socio)
"""

"""
if 'estabelecimento' in data and 'atividades_secundarias' in data['estabelecimento']:
    atividades_secundarias = data['estabelecimento']['atividades_secundarias']
    for atividade_secundaria in atividades_secundarias:
        atividade_secundaria['cnpj'] = data.get('estabelecimento', {}).get('cnpj', None)  # Track cnpj_raiz
        self.atividadesSecundariasList.append(atividade_secundaria)
"""