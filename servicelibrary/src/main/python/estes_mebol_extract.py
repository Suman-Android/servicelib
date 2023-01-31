import re

import traceback
from csv import writer
from address import AddressParser, Address
import os
import json
import pandas as pd
from types import SimpleNamespace

#cwd = os.getcwd()
# cwd = "/system/app/src/main/python"
# cwd = os.environ["HOME"]
customdir = os.path.dirname(__file__)
cwd = customdir
print(cwd)
print("Quasar: Version4, 31Jan23")

input_path = os.path.join(cwd, "routes", "estesBOL", "Input")
output_path = os.path.join(cwd, "routes", "estesBOL", "Output")
synfiles = os.path.join(cwd, "routes", "estesBOL", "Synonym")
status_path = os.path.join(cwd, "routes", "estesBOL", "AllFilesData.csv")
conf_files = os.path.join(cwd, "routes", "estesBOL", "Configuration")
constants_dict = os.path.join(cwd, "routes", "estesBOL", "Configuration", "Constants.txt")
field_prop_path = os.path.join(cwd, "routes", "estesBOL", "Configuration", "FieldProperties.txt")
pkg_type_path = os.path.join(cwd, "routes", "estesBOL", "Configuration", "PackageTypes.txt")

frame_right_cord = []
frame_bottom_cord = []


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

    max_right_Cord = max(frame_right_cord)
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

    max_right_Cord = max(frame_right_cord)
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

            if (not phoneMatch) & (not dateMatch) & (not row_word_match) & (
            not date_reg_ex_match):  # Changes as part of POC Phase 2, # Changes as part of POC Phase 2 V2
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


# Function to identify the label, row and bounding box of a given field in the document
def generic_field_label(header, synDict, docExtract, cord_range_ltrb):
    confine_label = ""
    confine_label_row = ""
    label_frame = {}

    max_right_cord = max(frame_right_cord)
    max_bottom_cord = max(frame_bottom_cord)

    for item in synDict[header]:
        if pd.notna(item):
            if item and item.strip():

                for textBlock in docExtract.textBlocks:
                    if item in str(textBlock.blockText):
                        for line in textBlock.lines:
                            if str(line.lineText).startswith(item):
                                if ((line.lineFrame.left > cord_range_ltrb[0] * max_right_cord) & (
                                        line.lineFrame.right < cord_range_ltrb[2] * max_right_cord)) & (
                                        (line.lineFrame.top > cord_range_ltrb[1] * max_bottom_cord) & (
                                        line.lineFrame.bottom < cord_range_ltrb[3] * max_bottom_cord)):

                                    confine_label = item
                                    confine_label_row = str(line.lineText)

                                    # To handle the field labels with multiple words
                                    item_word_list = item.split()
                                    for element in line.elements:
                                        # Identify the right bounding box of the last element of the item
                                        # if item_word_list[-1] == str(element.elemenText):
                                        if str(element.elemenText).startswith(item_word_list[-1]):
                                            label_end_frame = element.elementFrame.__dict__.copy()
                                            label_frame = line.lineFrame.__dict__.copy()
                                            label_frame["right"] = label_end_frame["right"]

                                            return confine_label, confine_label_row, label_frame

    return confine_label, confine_label_row, label_frame


# Function to identify the area of interest for a given field in the document
def area_interest(label_frame, bound_margin_ltrb, direction, rows):
    bound_area_interest = {
        "left": 0,
        "top": 0,
        "right": 0,
        "bottom": 0
    }

    if direction == "down":
        bound_area_interest["left"] = label_frame["left"] - bound_margin_ltrb[0]
        bound_area_interest["top"] = label_frame["bottom"]
        bound_area_interest["right"] = label_frame["right"] + bound_margin_ltrb[2]
        bound_area_interest["bottom"] = label_frame["bottom"] + (
                label_frame["bottom"] - label_frame["top"]) * rows + bound_margin_ltrb[3]

    return bound_area_interest


# Function to identify the elements of interest for a given field in the document
def elements_interest(field_area_interest, type_field, docExtract):
    elements_interest_list = []
    elements_int_conf_list = []

    for textBlock in docExtract.textBlocks:
        for line in textBlock.lines:
            for element in line.elements:
                if element.elementFrame.left >= field_area_interest["left"]:
                    if element.elementFrame.right <= field_area_interest["right"]:
                        if element.elementFrame.top >= field_area_interest["top"]:
                            if element.elementFrame.bottom <= field_area_interest["bottom"]:
                                # Handling of special characters in Decimal type fields
                                elements_interest_list.append(element.elemenText.replace("!", ".").replace("|", "").replace(",", ""))
                                elements_int_conf_list.append(element.elementConfidence)

    # print("Initial elements_interest_list:")
    # print(elements_interest_list)

    # if type_field.lower() == "decimal":
    for index, element_interest in reversed(list(enumerate(elements_interest_list))):
        try:
            element_interest = element_interest.replace("lbs", "")
            element_interest.strip()
            float(element_interest)
            if type_field.lower() == "string":
                elements_interest_list.pop(index)
                elements_int_conf_list.pop(index)
        except ValueError:
            if type_field.lower() == "decimal":
                elements_interest_list.pop(index)
                elements_int_conf_list.pop(index)

    return elements_interest_list, elements_int_conf_list


# Changes for addition of Confidence fields
# Function to extract the confidence score for a field
def fieldConfidence(doc, addressText, fieldValue):
    confidence = 0
    max_right_Cord = max(frame_right_cord)

    textTrim = os.linesep.join([s for s in addressText.splitlines() if s])
    splitlinelist = textTrim.splitlines()

    for i, word in enumerate(splitlinelist):
        xCord = 0

        for textBlock in doc.textBlocks:
            if fieldValue in str(textBlock.blockText):
                for line in textBlock.lines:
                    if fieldValue in str(line.lineText):
                        for element in line.elements:
                            if fieldValue == str(element.elemenText):
                                confidence = element.elementConfidence
                                xCord = line.lineCornerPoints[0].x

                            if (xCord > 0) & (xCord < (0.3402 * max_right_Cord)):
                                break

    return confidence


# Changes for addition of Confidence fields
# Function to extract the confidence score for OT_PRO field
def otproConfidence(doc, fieldValue):
    confidence = 0
    for textBlock in doc.textBlocks:
        if fieldValue in str(textBlock.blockText):
            for line in textBlock.lines:
                if fieldValue in str(line.lineText):
                    confidence = line.lineConfidence
                    # for element in line.elements:
                    #     if fieldValue in str(element.elemenText):
                    #         confidence = element.elementConfidence

    return confidence


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
        f = {"Status": "Processing", "Output": ""}
        with open(output_table_json, 'w') as outfile:
            json.dump(f, outfile)

        # Changes for addition of Confidence fields
        csv_row_data = [json_file, "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",
                        "-", "-", "-",
                        "Processing"]
        columns_names = ["DocName", "addressName_Shipper", "addressLine1_Shipper", "city_Shipper", "state_Shipper",
                         "zip_Shipper", "addressName_Consignee", "addressLine1_Consignee", "city_Consignee",
                         "state_Consignee", "zip_Consignee", "OT_PRO", "total_Weight", "handling_Units",
                         "packaging_Type", "state_Consignee_Confidence", "zip_Consignee_Confidence",
                         "OT_PRO_Confidence", "total_Weight_Confidence", "handling_Units_Confidence",
                         "packaging_Type_Confidence", "Status"]

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
        # Handling of Special Characters
        with open(input_file_path, 'r', encoding="utf-8") as document:
            # response = json.loads(document.read())
            doc = json.loads(document.read(), object_hook=lambda d: SimpleNamespace(**d))
        # doc = Document(response)
        # aws.processDocument(doc, output_temp_folder, os.path.join(input_folder_path, pdf_file))

        # print (doc)

        synDF = readsyndf(synfiles)
        key_dict = synDF.to_dict('list')

        constantsDict = readDataDict(constants_dict)
        field_prop_dict = readDataDict(field_prop_path)
        pkg_type_dict = readDataDict(pkg_type_path)

        # To calculate the rightmost and bottommost coordinate of the text
        for textBlock in doc.textBlocks:
            right_cord = textBlock.blockFrame.right
            bottom_cord = textBlock.blockFrame.bottom

            frame_right_cord.append(right_cord)
            frame_bottom_cord.append(bottom_cord)

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

        # Handling of Shipper Header at start of the document
        if originLabelRow in text:
            originIndex = text.index(originLabelRow)
        elif originLabelRow.lstrip() in text:
            originLabelRow = originLabelRow.lstrip()
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
                addressText = find_between(text, originLabelRow, destLabelRow, len(originLabel) + 1)
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

        # Changes for addition of Confidence fields
        address_text_shipper = addressText

        addressText = ""
        addressType = "Consignee"

        if (addressType == "Consignee"):
            if originIndex >= destIndex:
                addressText = find_between(text, destLabelRow, originLabelRow, len(destLabel) + 1)
            else:
                addressText = find_between(text, destLabelRow, '\n\n', len(destLabel) + 1)

            if (addressText):
                if (len(addressText) > 250):
                    state_zip_match = state_zip_reg_ex_prog.search(addressText)

                    if state_zip_match:
                        state_zip = state_zip_match.group(0)
                        state_zip_index = addressText.index(state_zip)
                        addressText = addressText[0:state_zip_index + len(state_zip)]
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

        # Changes for addition of Confidence fields
        address_text_consignee = addressText

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

        # Changes for addition of Confidence fields
        ot_pro_num_raw = ""

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

        # Data extraction for a Generic field - Changes start

        field_label = ""
        field_label_row = ""
        field_label_frame = {}
        field_area_interest = {}
        field_elements_interest = []
        field_elements_confidence = []

        # Default properties of a given field
        cord_range_field = field_prop_dict.get('cord_range_ltrb_def')
        bound_margin_field = field_prop_dict.get('bound_margin_ltrb_def')
        direction_field = field_prop_dict.get('direction_def')
        rows_field = field_prop_dict.get('rows_def')
        type_field = field_prop_dict.get('type_def')

        # Extraction of the Total Weight from a table in the document - Changes start
        if 'cord_range_ltrb_weight' in field_prop_dict:
            if field_prop_dict.get('cord_range_ltrb_weight'):
                cord_range_field = field_prop_dict.get('cord_range_ltrb_weight')

        if 'bound_margin_ltrb_weight' in field_prop_dict:
            if field_prop_dict.get('bound_margin_ltrb_weight'):
                bound_margin_field = field_prop_dict.get('bound_margin_ltrb_weight')

        if 'direction_weight' in field_prop_dict:
            if field_prop_dict.get('direction_weight') and field_prop_dict.get('direction_weight').strip():
                direction_field = field_prop_dict.get('direction_weight')

        if 'rows_weight' in field_prop_dict:
            if field_prop_dict.get('rows_weight'):
                rows_field = field_prop_dict.get('rows_weight')

        if 'type_weight' in field_prop_dict:
            if field_prop_dict.get('type_weight') and field_prop_dict.get('type_weight').strip():
                type_field = field_prop_dict.get('type_weight')

        field_label, field_label_row, field_label_frame = generic_field_label(
            "Weight", key_dict,
            doc,
            cord_range_field)

        # print("field_label: " + field_label)
        # print("field_label_row: " + field_label_row)
        # print("field_label_frame:")
        # print(field_label_frame)

        total_weight = ""
        total_weight_conf_score = ""
        if pd.notna(field_label):
            if field_label and field_label.strip():
                if bool(field_label_frame):
                    field_area_interest = area_interest(field_label_frame, bound_margin_field, direction_field,
                                                        rows_field)
                    # print("field_area_interest:")
                    # print(field_area_interest)

                    field_elements_interest, field_elements_confidence = elements_interest(field_area_interest,
                                                                                           type_field, doc)
                    # print("Final field_elements_interest:")
                    # print(field_elements_interest)

                    if field_elements_interest:
                        total_weight = str(field_elements_interest[-1])
                        total_weight_conf_score = str(field_elements_confidence[-1])
                    # print("total_weight: " + total_weight)
                    # print("total_weight_confidence: " + total_weight_conf_score)

        total_weight_details = {"total_Weight": total_weight}
        extractBOL.update(total_weight_details)

        # Extraction of the Total Weight from a table in the document - Changes end

        # Extraction of the Total Number of Handling Units from a table in the document - Changes start
        if 'cord_range_ltrb_units' in field_prop_dict:
            if field_prop_dict.get('cord_range_ltrb_units'):
                cord_range_field = field_prop_dict.get('cord_range_ltrb_units')

        if 'bound_margin_ltrb_units' in field_prop_dict:
            if field_prop_dict.get('bound_margin_ltrb_units'):
                bound_margin_field = field_prop_dict.get('bound_margin_ltrb_units')

        if 'direction_units' in field_prop_dict:
            if field_prop_dict.get('direction_units') and field_prop_dict.get('direction_units').strip():
                direction_field = field_prop_dict.get('direction_units')

        if 'rows_units' in field_prop_dict:
            if field_prop_dict.get('rows_units'):
                rows_field = field_prop_dict.get('rows_units')

        if 'type_units' in field_prop_dict:
            if field_prop_dict.get('type_units') and field_prop_dict.get('type_units').strip():
                type_field = field_prop_dict.get('type_units')

        field_label, field_label_row, field_label_frame = generic_field_label(
            "Units", key_dict,
            doc,
            cord_range_field)

        # print("field_label: " + field_label)
        # print("field_label_row: " + field_label_row)
        # print("field_label_frame:")
        # print(field_label_frame)

        total_units = ""
        total_units_conf_score = ""
        if pd.notna(field_label):
            if field_label and field_label.strip():
                if bool(field_label_frame):
                    field_area_interest = area_interest(field_label_frame, bound_margin_field, direction_field,
                                                        rows_field)
                    # print("field_area_interest:")
                    # print(field_area_interest)

                    field_elements_interest, field_elements_confidence = elements_interest(field_area_interest,
                                                                                           type_field, doc)
                    # print("Final field_elements_interest:")
                    # print(field_elements_interest)

                    if field_elements_interest:
                        total_units = str(field_elements_interest[-1])
                        total_units_conf_score = str(field_elements_confidence[-1])
                    # print("total_units: " + total_units)
                    # print("total_units_confidence: " + total_units_conf_score)

        total_units_details = {"handling_Units": total_units}
        extractBOL.update(total_units_details)

        # Extraction of the Total Number of Handling Units from a table in the document - Changes end

        # Extraction of the Packaging Type from a table/outside table in the document - Changes start
        if 'cord_range_ltrb_pkg' in field_prop_dict:
            if field_prop_dict.get('cord_range_ltrb_pkg'):
                cord_range_field = field_prop_dict.get('cord_range_ltrb_pkg')

        if 'bound_margin_ltrb_pkg' in field_prop_dict:
            if field_prop_dict.get('bound_margin_ltrb_pkg'):
                bound_margin_field = field_prop_dict.get('bound_margin_ltrb_pkg')

        if 'direction_pkg' in field_prop_dict:
            if field_prop_dict.get('direction_pkg') and field_prop_dict.get('direction_pkg').strip():
                direction_field = field_prop_dict.get('direction_pkg')

        if 'rows_pkg' in field_prop_dict:
            if field_prop_dict.get('rows_pkg'):
                rows_field = field_prop_dict.get('rows_pkg')

        if 'type_pkg' in field_prop_dict:
            if field_prop_dict.get('type_pkg') and field_prop_dict.get('type_pkg').strip():
                type_field = field_prop_dict.get('type_pkg')

        field_label, field_label_row, field_label_frame = generic_field_label(
            "Piece Type", key_dict,
            doc,
            cord_range_field)

        # print("field_label: " + field_label)
        # print("field_label_row: " + field_label_row)
        # print("field_label_frame:")
        # print(field_label_frame)

        pkg_type = ""
        pkg_type_conf_score = ""
        if pd.notna(field_label):
            if field_label and field_label.strip():
                if bool(field_label_frame):
                    field_area_interest = area_interest(field_label_frame, bound_margin_field, direction_field,
                                                        rows_field)
                    # print("field_area_interest:")
                    # print(field_area_interest)

                    field_elements_interest, field_elements_confidence = elements_interest(field_area_interest,
                                                                                           type_field, doc)
                    # print("Final field_elements_interest:")
                    # print(field_elements_interest)

                    if field_elements_interest:
                        for field_element, field_element_conf in zip(field_elements_interest,
                                                                     field_elements_confidence):
                            if field_element in pkg_type_dict:
                                pkg_type = field_element.upper()
                                pkg_type_conf_score = str(field_element_conf)
                                break
                            elif field_element in pkg_type_dict.values():
                                pkg_type = field_element.upper()
                                pkg_type_conf_score = str(field_element_conf)
                                break

        if not pkg_type and not pkg_type.strip():
            break_out_flag = False
            for pkg_type_key in pkg_type_dict:
                for textBlock in doc.textBlocks:
                    if pkg_type_key.lower() in textBlock.blockText.lower():
                        for line in textBlock.lines:
                            if line.lineText.lower().startswith(pkg_type_key.lower()):
                                # print(pkg_type_key)
                                for element in line.elements:
                                    if pkg_type_key.lower() == element.elemenText.lower():
                                        pkg_type = pkg_type_key.upper()
                                        pkg_type_conf_score = str(element.elementConfidence)
                                        break_out_flag = True
                                        break
                                if break_out_flag:
                                    break
                        if break_out_flag:
                            break

                    elif pkg_type_dict[pkg_type_key] in textBlock.blockText:
                        for line in textBlock.lines:
                            if line.lineText.startswith(pkg_type_dict[pkg_type_key]):
                                # print(pkg_type_dict[pkg_type_key])
                                for element in line.elements:
                                    if pkg_type_dict[pkg_type_key] == element.elemenText:
                                        pkg_type = pkg_type_key.upper()
                                        pkg_type_conf_score = str(element.elementConfidence)
                                        break_out_flag = True
                                        break
                                if break_out_flag:
                                    break
                        if break_out_flag:
                            break
                if break_out_flag:
                    break

        # print("pkg_type: " + pkg_type)

        pkg_type_details = {"packaging_Type": pkg_type}
        extractBOL.update(pkg_type_details)

        # Extraction of the Packaging Type from a table/outside table in the document - Changes end

        # Data extraction for a Generic field - Changes end

        # Changes for addition of Confidence fields start
        # Confidence score for Consignee State
        state_cons_conf_score = ""
        state_cons_val = extractBOL["state_Consignee"]
        if pd.notna(state_cons_val):
            if state_cons_val and state_cons_val.strip():
                state_cons_conf_score = fieldConfidence(doc, address_text_consignee, state_cons_val)

        state_consignee_conf = {"state_Consignee_Confidence": str(state_cons_conf_score)}
        extractBOL.update(state_consignee_conf)

        # Confidence score for Consignee Zip
        zip_cons_conf_score = ""
        zip_cons_val = extractBOL["zip_Consignee"]
        if pd.notna(zip_cons_val):
            if zip_cons_val and zip_cons_val.strip():
                zip_cons_conf_score = fieldConfidence(doc, address_text_consignee, zip_cons_val)

        zip_consignee_conf = {"zip_Consignee_Confidence": str(zip_cons_conf_score)}
        extractBOL.update(zip_consignee_conf)

        # Confidence score for OT_PRO
        ot_pro_conf_score = ""
        # print(ot_pro_num_raw)
        if pd.notna(ot_pro_num_raw):
            if ot_pro_num_raw and ot_pro_num_raw.strip():
                ot_pro_conf_score = otproConfidence(doc, ot_pro_num_raw)

        ot_pro_conf = {"OT_PRO_Confidence": str(ot_pro_conf_score)}
        extractBOL.update(ot_pro_conf)

        # Extraction of confidence score for 3 more fields
        # Confidence score for Total Weight
        total_weight_conf = {"total_Weight_Confidence": str(total_weight_conf_score)}
        extractBOL.update(total_weight_conf)

        # Confidence score for Handling Units
        total_units_conf = {"handling_Units_Confidence": str(total_units_conf_score)}
        extractBOL.update(total_units_conf)

        # Confidence score for Packaging Type
        pkg_type_conf = {"packaging_Type_Confidence": str(pkg_type_conf_score)}
        extractBOL.update(pkg_type_conf)
        # Changes for addition of Confidence fields end

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
        # return resultExtractBOL
        return json.dumps(resultExtractBOL)  # Change in application response type to JSON

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
        # return f
        return json.dumps(f)  # Change in application response type to JSON


# Main function of the ESTES EBOL Mobile App
def main(file_name):
    return extract(input_path, output_path, file_name)
