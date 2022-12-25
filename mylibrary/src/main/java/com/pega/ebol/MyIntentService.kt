package com.pega.ebol

import android.app.IntentService
import android.content.Intent
import android.util.Log
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MyIntentService() : IntentService("name") {
    override fun onHandleIntent(p0: Intent?) {
        Log.e("MyIntentService", "Hello from Service")
        try {
            if (!Python.isStarted()){
                Python.start(AndroidPlatform(this))
            }
            val py = Python.getInstance()
            val data = py.getModule("estes_mebol_extract").callAttr("main", "NewMLData.json")
            Log.e("MyIntentService", data.toString())
        } catch (e: Exception) {
            e.printStackTrace()
            Log.e("MyIntentService", e.localizedMessage)
        }
    }
}