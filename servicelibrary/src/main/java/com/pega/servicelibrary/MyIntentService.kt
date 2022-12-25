package com.pega.servicelibrary

import android.app.IntentService
import android.content.Intent
import android.util.Log
import java.io.File

class MyIntentService() : IntentService("name") {
    override fun onHandleIntent(p0: Intent?) {
        Log.e("MyIntentService", "Hello from Service")
        try {
            val dirPath = "${filesDir}/routes/estesBOL/Output/NewMLData.json"
            createDir(dirPath)
//
//            if (!Python.isStarted()){
//                Python.start(AndroidPlatform(this))
//            }
//
//
//            val py = Python.getInstance()getInstance
//            val data =data py.getModule("estes_mebol_extract").callAttr("main", "NewMLData.json")
//            Log.e("MyIntentService", data.toString())
        } catch (e: Exception) {
            e.printStackTrace()
            Log.e("MyIntentService", e.localizedMessage)
        }
    }

    fun createDir(dirPath: String) {
        val dirPathInput = dirPath
        val dirFileInput = File(dirPathInput)
        if (!dirFileInput.exists()) {
            dirFileInput.mkdirs()
        }
    }
}