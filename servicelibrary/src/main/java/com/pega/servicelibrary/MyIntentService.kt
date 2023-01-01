package com.pega.servicelibrary

import android.app.IntentService
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Log
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.File

lateinit var resultReceiverCallBack: ResultReceiverCallBack

class MyIntentService : IntentService("name") {

    companion object {
        internal const val IMAGE_NAME = "image_name"
        internal const val TAG = "MyIntentService"
    }

    override fun onHandleIntent(intent: Intent?) {
        try {
            Log.e(TAG, "Hello from Service")
            val imageName = intent?.getStringExtra(IMAGE_NAME).toString()
            val fileName = imageName.split(".")[0] + ".json"
            Log.e(TAG, "Image Name $imageName")
            Log.e(TAG, "File Name $fileName♥")
            val pegaFile: File = File("${filesDir}/ClientStore/$imageName")
            if (pegaFile.exists()) {
                Log.e(TAG, pegaFile.path.toString() + " " + pegaFile.exists().toString())
                val capturedBitmap = getBitmap(pegaFile)
                val byteArrayOutputStream = ByteArrayOutputStream()
                capturedBitmap!!.compress(Bitmap.CompressFormat.JPEG, 90, byteArrayOutputStream)
                val inputImage: InputImage = InputImage.fromBitmap(capturedBitmap, 0)
                getTextRecognise(inputImage,fileName)
            } else {
                resultReceiverCallBack?.onError("File Not Found")
            }
        } catch (e: Exception) {
            e.printStackTrace()
            resultReceiverCallBack?.onError(e.localizedMessage)
        }
    }

    fun createDir(dirPath: String) {
        val dirPathInput = dirPath
        val dirFileInput = File(dirPathInput)
        if (!dirFileInput.exists()) {
            dirFileInput.mkdirs()
        }
    }

    private fun getTextRecognise(image: InputImage, fileName: String) {
        var finalResult = ""
        val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
        recognizer.process(image).addOnSuccessListener { result ->
            try {
                Log.e(TAG, "TextRecognitionData " + result.textBlocks.toString())
                var jsonObjectresultText = JSONObject()
                jsonObjectresultText.put(
                    "resultText", result.text.replace("\n", "FGMLKITND").replace("\"", "")
                )

                var jsonArrayblock = ArrayList<JSONObject>()

                for (block in result.textBlocks) {
                    var jsonArrayblockcornerPoints = ArrayList<JSONObject>()
                    var jsonObjecttextBlocks = JSONObject()

                    jsonObjecttextBlocks.put(
                        "blockText", block.text.replace("\n", "FGMLKITND").replace("\"", "")
                    )

                    var jsonObjectblockboundingBox = JSONObject()

                    jsonObjectblockboundingBox.put("bottom", block.boundingBox?.bottom)
                    jsonObjectblockboundingBox.put("left", block.boundingBox?.left)
                    jsonObjectblockboundingBox.put("right", block.boundingBox?.right)
                    jsonObjectblockboundingBox.put("top", block.boundingBox?.top)

                    jsonObjecttextBlocks.put("blockFrame", jsonObjectblockboundingBox)


                    if (block.cornerPoints != null) {
                        for (cornerPoints in block.cornerPoints!!) {
                            var blockcornerPoints = JSONObject()
                            blockcornerPoints.put("x", cornerPoints.x)
                            blockcornerPoints.put("y", cornerPoints.y)
                            jsonArrayblockcornerPoints.add(blockcornerPoints)
                        }
                    }
                    jsonObjecttextBlocks.put("blockCornerPoint", jsonArrayblockcornerPoints)

                    var jsonArraylines = ArrayList<JSONObject>()
                    var jsonArraylinecornerPoints = ArrayList<JSONObject>()

                    for (line in block.lines) {

                        var jsonObjectline = JSONObject()
                        jsonObjectline.put(
                            "lineText", line.text.replace("\n", "FGMLKITND").replace("\"", "")
                        )
                        jsonObjectline.put("lineConfidence", line.confidence)
                        var lineboundingBox = JSONObject()
                        lineboundingBox.put("bottom", line.boundingBox?.bottom)
                        lineboundingBox.put("right", line.boundingBox?.right)
                        lineboundingBox.put("top", line.boundingBox?.top)
                        lineboundingBox.put("left", line.boundingBox?.left)

                        jsonObjectline.put("lineFrame", lineboundingBox)

                        if (line.cornerPoints != null) {
                            for (cornerPoints in line.cornerPoints!!) {
                                var linecornerPoints = JSONObject()
                                linecornerPoints.put("x", cornerPoints.x)
                                linecornerPoints.put("y", cornerPoints.y)
                                jsonArraylinecornerPoints.add(linecornerPoints)


                            }
                        }
                        jsonObjectline.put("lineCornerPoints", jsonArraylinecornerPoints)
                        var jsonArray = ArrayList<JSONObject>()
                        var jsonArrayelementcornerPoints = ArrayList<JSONObject>()
                        for (element in line.elements) {

                            var jsonObjectelement = JSONObject()

                            jsonObjectelement.put(
                                "elemenText",
                                element.text.replace("\n", "FGMLKITND").replace("\"", "")
                            )
                            jsonObjectelement.put("elementConfidence", element.confidence)

                            var elementboundingBox = JSONObject()

                            elementboundingBox.put("bottom", element.boundingBox?.bottom)
                            elementboundingBox.put("right", element.boundingBox?.right)
                            elementboundingBox.put("top", element.boundingBox?.top)
                            elementboundingBox.put("left", element.boundingBox?.left)

                            jsonObjectelement.put("elementFrame", elementboundingBox)

                            if (element.cornerPoints != null) {
                                for (elementPoints in element.cornerPoints!!) {
                                    var jsonObjectelementcornerPoints = JSONObject()
                                    jsonObjectelementcornerPoints.put("y", elementPoints.y)
                                    jsonObjectelementcornerPoints.put("x", elementPoints.x)
                                    jsonArrayelementcornerPoints.add(jsonObjectelementcornerPoints)
                                }
                            }
                            // jsonArrayelementcornerPoints.add(jsonArray.toString().replace("\\",""))
                            jsonObjectelement.put(
                                "elementCornerPoints",
                                jsonArrayelementcornerPoints
                            )
                            jsonArray.add(jsonObjectelement)
                        }

                        jsonObjectline.put("elements", jsonArray)
                        jsonArraylines.add(jsonObjectline)
                    }

                    jsonObjecttextBlocks.put("lines", jsonArraylines)
                    jsonArrayblock.add(jsonObjecttextBlocks)


                }

                jsonObjectresultText.put("textBlocks", jsonArrayblock)
//            Log.e(TAG, jsonObjectresultText.toString())

                val dirPathInput =
                    "${filesDir}/chaquopy/AssetFinder/app/routes/estesBOL/Input"

                val xmlFile: File = File(dirPathInput + "/$fileName")
                xmlFile.writeText(
                    jsonObjectresultText.toString().replace("\\", "").replace("]\"", "]")
                        .replace("\"[", "[").replace("FGMLKITND", "\\n")
                )
                getPythonExtraction(fileName)
            } catch (e: Exception) {
                e.printStackTrace()
                resultReceiverCallBack?.onError(e.localizedMessage)
            }
        }.addOnFailureListener { e ->
            // Task failed with an exception
            Log.e(TAG, e.message.toString())
            resultReceiverCallBack?.onError(e.localizedMessage)
        }
    }

    fun getBitmap(pegaFile: File): Bitmap? {
        return BitmapFactory.decodeFile(pegaFile.path)
    }

    fun getPythonExtraction(fileName: String) {
        try {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(applicationContext))
            }
            val py = Python.getInstance()
            val extractPythonData =
                py.getModule("estes_mebol_extract").callAttr("main", fileName)
            Log.i(TAG, extractPythonData.toString())
            resultReceiverCallBack?.onSuccess(extractPythonData.toString())
        } catch (e: Exception) {
            e.printStackTrace()
            Log.e(TAG, e.message.toString())
            resultReceiverCallBack?.onError(e.localizedMessage)
        }
    }


    fun startServiceForPython(
        context: Context,
        imageName: String,
        _resultReceiverCallBack: ResultReceiverCallBack
    ) {
        resultReceiverCallBack = _resultReceiverCallBack
        val intent = Intent(context, MyIntentService::class.java)
        intent.putExtra(IMAGE_NAME, imageName)
        context.startService(intent)
    }

}