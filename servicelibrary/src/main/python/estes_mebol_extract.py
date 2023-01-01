import re

import traceback
from csv import writer
from address import AddressParser, Address
import os
import json
import pandas as pd
from types import SimpleNamespace

# cwd = "/system/app/src/main/python"
# cwd = os.environ["HOME"]
customdir = os.path.dirname(__file__)
print("Custom Dir New " + customdir)
cwd = customdir
print(cwd)
input_path = os.path.join(cwd, "routes", "estesBOL", "Input")
output_path = os.path.join(cwd, "routes", "estesBOL", "Output")
synfiles = os.path.join(cwd, "routes", "estesBOL", "Synonym")
status_path = os.path.join(cwd, "routes", "estesBOL", "AllFilesData.csv")
conf_files = os.path.join(cwd, "routes", "estesBOL", "Configuration")
constants_dict = os.path.join(cwd, "routes", "estesBOL", "Configuration", "Constants.txt")
frame_right_Cord = []


def readsyndf(synfiles):
    for synfile in os.listdir(synfiles):
        synDF = pd.read_csv(synfiles + '/' + synfile)
        return synDF

def readDataDict(dataDictFile):
    with open(dataDictFile) as f:
        data = f.read()

    dataDict = json.loads(data)
    return dataDict


def remove_items(test_list, item):
    res = [i for i in test_list if i != item]
    return res

def find_between(rawText, startStr, endStr, startStrLen):
    try:
        start = rawText.index(startStr) + startStrLen
        end = rawText.index(endStr, start)
        return rawText[start:end]
    except ValueError:
        return ""


def addressLabel(header, synDict, rawText, docExtract):
    confineLabel = ""
    confineLabelRow = ""

    max_right_Cord = max(frame_right_Cord)
    # print(max_right_Cord)

    for item in synDict[header]:
        # NA values, such as None or numpy.NaN, get mapped to False values
        # Empty strings '' are not considered NA values
        if (pd.notna(item)):
            if item and item.strip():  # item is not None AND item is not empty or blank
                for i, word in enumerate(rawText.splitlines()):
                    if word.startswith(item):
                        # print(item)
                        xCord = 0
                        yCord = 0
                        xCord, yCord = addressLabelCord(docExtract, word)[0]
                        if (xCord < (0.4 * max_right_Cord)) & (yCord < (0.5 * max_right_Cord)):
                            confineLabel = item
                            confineLabelRow = word
                            return confineLabel, confineLabelRow

    return confineLabel, confineLabelRow


def addressLabelCord(doc, word):
    pageNumber = 1
    cordList = []
    xCord = 0
    yCord = 0
    # print(word)
    # for page in doc.pages:
    for textBlock in doc.textBlocks:
        # for line in page.lines:
        for line in textBlock.lines:
            # if (str(line.text) == word):
            if (str(line.lineText) == word):
                # xCord = line.geometry.boundingBox.left
                xCord = line.lineCornerPoints[0].x
                # yCord = line.geometry.boundingBox.top
                yCord = line.lineCornerPoints[0].y
                cordList.append([xCord, yCord])
                # print(cordList)
        pageNumber = pageNumber + 1

    return cordList


def addressExtract(doc, addressText, constantsDict):

    textTrim = os.linesep.join([s for s in addressText.splitlines() if s])
    splitlinelist = textTrim.splitlines()
    addressParse = ""

    phoneRegExpr = '^(?:\([2-9]\d{2}\)\ ?|[2-9]\d{2}(?:\-?|\ ?))[2-9]\d{2}[- ]?\d{4}$'
    phoneRegExprProg = re.compile(phoneRegExpr)

    # To identify zip codes of 5+4 format
    zip_plus_reg_ex = '\d{5}(?:[-\s]\d{4})'
    zip_plus_reg_ex_prog = re.compile(zip_plus_reg_ex)
    zip_plus_four_code = None

    # To identify date format strings
    date_reg_expr = '^[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2}$'
    date_reg_expr_prog = re.compile(date_reg_expr)

    max_right_Cord = max(frame_right_Cord)
    # print(max_right_Cord)

    for i, word in enumerate(splitlinelist):
        pageNumber = 1
        xCord = 0
        # for page in doc.pages:
        for textBlock in doc.textBlocks:
            # for line in page.lines:
            for line in textBlock.lines:
                # if str(line.text) == word:
                if str(line.lineText) == word:
                    # xCord = line.geometry.boundingBox.left
                    xCord = line.lineCornerPoints[0].x

                if (xCord > 0) & (xCord < (0.3402 * max_right_Cord)):
                    break

            pageNumber = pageNumber + 1

        # if xCord < 0.35:
        if xCord < (0.3402 * max_right_Cord):

            phoneMatch = phoneRegExprProg.match(word)

            # To identify zip codes of 5+4 format
            zip_plus_match = zip_plus_reg_ex_prog.search(word)
            if zip_plus_match:
                zip_plus_four_code = zip_plus_match.group(0)

            # To remove Ship Date, Due Date, etc from Address
            dateMatch = False
            if "date" in word.lower():
                dateMatch = True

            # For stripping a row from address
            row_word_match = False
            for item in constantsDict.get('address_strip_row_word'):
                if item in word:
                    row_word_match = True

            date_reg_ex_match = date_reg_expr_prog.match(word)

            if (not phoneMatch) & (not dateMatch) & (not row_word_match) & (not date_reg_ex_match):  # Changes as part of POC Phase 2, # Changes as part of POC Phase 2 V2
                addressParse = addressParse + word + str(", ")

    addressParse = addressParse[:len(addressParse) - 2]

    addressParseUpdate = addressParse.replace(constantsDict.get('address_skip_text'), '')

    # For stripping a word from address
    for item in constantsDict.get('address_strip_word'):
        addressParseUpdate = addressParseUpdate.replace(item, '')

    addressParseSplit = [x.strip() for x in addressParseUpdate.split(', ')]

    for item in constantsDict.get('address_skip_row'):
        addressParseSplit = remove_items(addressParseSplit, item)

    addressParseClean = ", ".join(addressParseSplit)
    # print(addressParseClean)

    addressDetailsShipper = ""
    ap = AddressParser()
    address = ap.parse_address("")
    addressCity = ""
    if addressParseClean:
        address = ap.parse_address(addressParseClean)
        result = {}
        result["full_address"] = address.full_address()
        result["buiding"] = address.building
        result["city"] = address.city
        result["state"] = address.state
        result["zip"] = address.zip

        if zip_plus_four_code is not None:

            # Previous character of zip_plus_four_code should be space
            zip_plus_four_index = addressParseClean.find(zip_plus_four_code)
            if addressParseClean[zip_plus_four_index - 1] == ' ':
                address.zip = zip_plus_four_code

        zipIndex = 0
        if address.zip:
            for i, word in enumerate(addressParseSplit):
                if str(address.zip) in word:
                    zipIndex = i
            addressCity = addressParseSplit[zipIndex - 1]
        else:
            if len(addressParseSplit) > 2:
                addressCity = addressParseSplit[2]

    return addressParseSplit, address, addressCity



# Function to extract Key Value pairs from EBOL documents
def extract(input_folder_path, output_folder_path, json_file):
    try:
        if not json_file.endswith(".json"):
            raise Exception('Document submitted is not a JSON !!!')

        output_temp_folder = os.path.join(output_folder_path, json_file)
        # Create temp folder
        if os.path.exists(os.path.join(output_temp_folder)) is False:
            os.mkdir(output_temp_folder)
        else:
            pass

        output_table_json = os.path.join(output_temp_folder, "output_table_json.json")
        f = {"Status" : "Processing", "Output" : ""}
        with open(output_table_json, 'w') as outfile:
            json.dump(f, outfile)

        csv_row_data = [json_file, "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "Processing"]
        columns_names = ["DocName", "addressName_Shipper", "addressLine1_Shipper", "city_Shipper", "state_Shipper",
                         "zip_Shipper", "addressName_Consignee", "addressLine1_Consignee", "city_Consignee",
                         "state_Consignee", "zip_Consignee", "OT_PRO", "Status"]

        if os.path.exists(status_path):
            presentDf = pd.read_csv(status_path, index_col=False)
            if len(presentDf.loc[presentDf.DocName == json_file]) == 0:
                with open(status_path, 'a', newline='') as f_object:
                    writer_object = writer(f_object)
                    writer_object.writerow(csv_row_data)
                    f_object.close()
        else:
            final_df = pd.DataFrame(columns=columns_names, dtype=object)
            final_df.loc[0] = csv_row_data
            final_df.to_csv(status_path, index=False)

        # # Extract text from pdf if not available
        # aws_json_path = os.path.join(output_temp_folder,  "aws_extract.json")
        # if os.path.exists(aws_json_path) is False:
        #     aws.aws_main_call(output_temp_folder, os.path.join(input_folder_path, pdf_file))

        # parse json data
        input_file_path = os.path.join(input_folder_path, json_file)
        # with open(aws_json_path, 'r') as document:
        with open(input_file_path, 'r') as document:
            # response = json.loads(document.read())
            doc = json.loads(document.read(), object_hook=lambda d: SimpleNamespace(**d))
        # doc = Document(response)
        # aws.processDocument(doc, output_temp_folder, os.path.join(input_folder_path, pdf_file))

        # print (doc)

        synDF = readsyndf(synfiles)
        key_dict = synDF.to_dict('list')

        constantsDict = readDataDict(constants_dict)

        # To calculate the rightmost x cordinate of the text
        for textBlock in doc.textBlocks:
            rightCord = textBlock.blockFrame.right
            frame_right_Cord.append(rightCord)


        # aws_json_path = os.path.join(output_temp_folder,  "aws_raw_text.txt")
        # with open(aws_json_path, 'r') as file:
        #     text = file.read()
        #     text = unidecode.unidecode(text)
        text = doc.resultText + "\n\n"


        originLabel = ""
        originLabelRow = ""
        destLabel = ""
        destLabelRow = ""

        originEndLabel = ""
        originEndLabelRow = ""

        # specialInstLabel = ""
        originIndex = 0
        destIndex = 0
        originEndIndex = 0

        originLabel, originLabelRow = addressLabel("Origin Address", key_dict, text, doc)
        destLabel, destLabelRow = addressLabel("Destination Address", key_dict, text, doc)
        originEndLabel, originEndLabelRow = addressLabel("Origin Address End", key_dict, text, doc)

        originLabelRow = '\n' + originLabelRow + '\n'
        destLabelRow = '\n' + destLabelRow + '\n'
        originEndLabelRow = '\n' + originEndLabelRow + '\n'

        originIndex = text.index(originLabelRow)
        destIndex = text.index(destLabelRow)

        if (len(originEndLabelRow.strip()) > 0):
            originEndIndex = text.index(originEndLabelRow)

        # To identify US State and Zip code
        state_zip_reg_ex = '(?<![A-Za-z0-9])[A-Z]{2}[ .]+\d{5}(?:[- ]+\d{4})?[ \n]'
        state_zip_reg_ex_prog = re.compile(state_zip_reg_ex)
        state_zip = ""

        addressDetailsShipper = ""
        addressDetailsConsignee = ""

        addressText = ""
        addressType = "Shipper"

        if (addressType == "Shipper"):
            if originIndex < destIndex:
                addressText = find_between(text, originLabelRow, destLabelRow, len(originLabel)+1)
            else:
                if originEndIndex > 0:
                    addressText = find_between(text, originLabelRow, originEndLabelRow, len(originLabel) + 1)
                else:
                    addressText = find_between(text, originLabelRow, '\n\n', len(originLabel) + 1)

            if (addressText):
                if (originLabelRow == '\n\n') | (len(addressText) > 250):
                    addressText = addressText[0:250]

                addressParseSplit = []
                addressParseSplit, address, addressCity = addressExtract(doc, addressText, constantsDict)

                addressDetailsShipper = {
                    "addressName_" + addressType: addressParseSplit[0] if len(addressParseSplit) > 0 else "",
                    "addressLine1_" + addressType: addressParseSplit[1] if len(addressParseSplit) > 1 else "",
                    "city_" + addressType: addressCity,
                    "state_" + addressType: address.state,
                    "zip_" + addressType: address.zip}
            else:
                addressDetailsShipper = {"addressName_" + addressType: "",
                                         "addressLine1_" + addressType: "",
                                         "city_" + addressType: "",
                                         "state_" + addressType: "",
                                         "zip_" + addressType: ""}

        addressText = ""
        addressType = "Consignee"

        if (addressType == "Consignee"):
            if originIndex >= destIndex:
                addressText = find_between(text, destLabelRow, originLabelRow, len(destLabel) + 1)
            else:
                addressText = find_between(text, destLabelRow, '\n\n', len(destLabel) + 1)


            if(addressText):
                if (len(addressText) > 250):
                    state_zip_match = state_zip_reg_ex_prog.search(addressText)

                    if state_zip_match:
                        state_zip = state_zip_match.group(0)
                        state_zip_index = addressText.index(state_zip)
                        addressText = addressText[0:state_zip_index+len(state_zip)]
                    else:
                        addressText = addressText[0:250]

                addressParseSplit = []
                addressParseSplit, address, addressCity = addressExtract(doc, addressText, constantsDict)

                addressDetailsConsignee = {
                    "addressName_" + addressType: addressParseSplit[0] if len(addressParseSplit) > 0 else "",
                    "addressLine1_" + addressType: addressParseSplit[1] if len(addressParseSplit) > 1 else "",
                    "city_" + addressType: addressCity,
                    "state_" + addressType: address.state,
                    "zip_" + addressType: address.zip}
            else:
                addressDetailsConsignee = {"addressName_" + addressType: "",
                                           "addressLine1_" + addressType: "",
                                           "city_" + addressType: "",
                                           "state_" + addressType: "",
                                           "zip_" + addressType: ""}


        addressDetailsShipperStr = json.dumps(addressDetailsShipper)
        extractBOL = json.loads(addressDetailsShipperStr)

        # extractBOL.update(addressDetailsShipper)
        extractBOL.update(addressDetailsConsignee)


        # To identify OT_PRO number
        ot_pro_reg_ex = '\d{3}(\s*?)-(\s*?)\d{7}'
        ot_pro_reg_ex_1 = '011\d{7}'
        ot_pro_reg_ex_prog = re.compile(ot_pro_reg_ex)
        ot_pro_reg_ex_1_prog = re.compile(ot_pro_reg_ex_1)
        ot_pro_num = ""

        ot_pro_match = ot_pro_reg_ex_prog.search(text)
        if ot_pro_match:
            ot_pro_num_raw = ot_pro_match.group(0)
            ot_pro_num = ot_pro_num_raw.replace(" ", "").replace("-", "").strip()
        else:
            ot_pro_match = ot_pro_reg_ex_1_prog.search(text)
            if ot_pro_match:
                ot_pro_num_raw = ot_pro_match.group(0)
                ot_pro_num = ot_pro_num_raw.replace(" ", "").replace("-", "").strip()

        ot_pro_num_details = {"OT_PRO": ot_pro_num}
        extractBOL.update(ot_pro_num_details)

        # Extraction of OT_PRO number end

        print(json.dumps(extractBOL))

        resultExtractBOL = {"Status": "Success", "Output": [extractBOL]}
        with open(output_table_json, 'w') as outfile:
            json.dump(resultExtractBOL, outfile, indent=4)

        # CSV data hanling start
        csv_row_data = []
        for key in extractBOL:
            csv_row_data.append(extractBOL[key])

        # csv_row_data = [1.0, "1", "Pallets ", "6 doors/6 frames/hardware - 88.0 x 360x 30.0 ", "70.0", False, "983", "Mesker Southeast", "710 South Powerline Road Suite E", "Deerfield Bch", "FL", "33442"]
        # csv_row_data = get_extraction(raw_text_data)
        csv_row_data.insert(0, json_file)
        # print(csv_row_data)
        condition_match = True
        if condition_match is True:
            csv_row_data.append("Pending")
            presentDf = pd.read_csv(status_path, index_col=False)
            # print(csv_row_data)
            presentDf.loc[presentDf.DocName == json_file] = [csv_row_data]
            presentDf.to_csv(status_path, index=False)
            csv_row_data.pop()
            columns_names.pop()
            # final_df = pd.DataFrame(columns=columns_names, index=[0])
            final_df = pd.DataFrame(columns=columns_names, dtype=object)
            final_df.loc[0] = csv_row_data
            # print(final_df)
            final_df.to_csv(os.path.join(output_folder_path, json_file, "output_csv.csv"), index=False)
            f = {"Status": "Success", "Output": json.loads(final_df.to_json(orient='records'))}
            with open(output_table_json, 'w') as outfile:
                json.dump(f, outfile, indent=4)
        else:
            csv_row_data.pop()
            csv_row_data.append("Failed")
            # print(csv_row_data)
            presentDf = pd.read_csv(status_path, index_col=False)
            presentDf.loc[presentDf.DocName == json_file] = [csv_row_data]
            presentDf.to_csv(status_path, index=False)
            f = {"Status": "Faild", "Output": []}
            with open(output_table_json, 'w') as outfile:
                json.dump(f, outfile, indent=4)
        # CSV data handling end

        # return "Success"
        return resultExtractBOL

    except Exception as e:
        print("Unable to process")
        print(traceback.format_exc())

        # CSV data hanling start
        csv_row_data.pop()
        csv_row_data.append("Failed")
        presentDf = pd.read_csv(status_path, index_col=False)
        presentDf.loc[presentDf.DocName == json_file] = [csv_row_data]
        presentDf.to_csv(status_path, index=False)
        f = {"Status": "Failed", "Output": []}
        with open(output_table_json, 'w') as outfile:
            json.dump(f, outfile, indent=4)
        # CSV data handling end

        # f = {"Status": "Failed", "Output": ""}
        # with open(output_table_json, 'w') as outfile:
        #     json.dump(f, outfile, indent=4)
        return f

# Main function of the ESTES EBOL Mobile App
def main (file_name):

    return extract(input_path, output_path, file_name)
