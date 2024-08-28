import os
import json
import dotenv
import pandas as pd

class JsonConverter:

    SOCIOS = 'socios'
    ESTABELECIMENTO = 'estabelecimento'
    ATIVIDADES_SECUNDARIAS = 'atividades_secundarias'
    CNPJ = 'cnpj'
    SAVED = "saved"

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

    def renameJSONFiles(self):
        for jsonFileName in os.listdir(self.subfolder):
            if self.SAVED not in jsonFileName and jsonFileName.endswith('.json'):
                originalFilePath = os.path.join(self.subfolder, jsonFileName)
                # Create new filename with '-saved' suffix
                name, ext = os.path.splitext(jsonFileName)
                savedFileName = f'{name}-{self.SAVED}{ext}'
                savedFilePath = os.path.join(self.subfolder, savedFileName)
                try:
                    # Rename the file
                    os.rename(originalFilePath, savedFilePath)
                    print(f"Renamed {jsonFileName} to {savedFileName}")
                except Exception as e:
                    print(f"Error renaming {jsonFileName}: {e}")
    
    def readJSONSubfolder(self):
        
        for jsons in os.listdir(self.subfolder):
            if self.SAVED not in jsons:
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

        if not self.dfList:
            return pd.DataFrame()

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

    def incrementalDFToExcel(self):
        oldGeneralDF = pd.read_excel(io=self.generalFileName)
        concatGeneralDF = pd.concat([oldGeneralDF, self.df], axis=0, ignore_index=True)
        concatGeneralDF.to_excel(self.generalFileName, index=False)

    def incrementalSociosDfToExcel(self):
        oldSociosDF = pd.read_excel(io=self.socioFileName)
        concatSociosDF = pd.concat([oldSociosDF, self.socios], axis = 0, ignore_index=True)
        concatSociosDF.to_excel(self.socioFileName, index=False)

    def incrementalAtividadesSecundariasToExcel(self):
        oldAtividadesDF = pd.read_excel(io=self.atividadesSecundariasFileName)
        concatAtividadesDF = pd.concat([oldAtividadesDF, self.atividadesSecundarias], axis = 0, ignore_index=True)
        concatAtividadesDF.to_excel(self.atividadesSecundariasFileName, index=False)
        
    def firstSaveExcel(self):
        if not self.df.empty:
            self.dfToExcel()
            self.sociosDfToExcel()
            self.atividadesSecundariasToExcel()
            self.renameJSONFiles()
        else:
            pass

    def incrementalSaveExcel(self):
        if not self.df.empty:
            self.incrementalDFToExcel()
            self.incrementalSociosDfToExcel()
            self.incrementalAtividadesSecundariasToExcel()
            self.renameJSONFiles()
        else:
            pass

teste = JsonConverter()
print(teste.socios)