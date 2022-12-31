package com.pega.moduledemo

import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.pega.servicelibrary.MyIntentService
import com.pega.servicelibrary.ResultReceiverCallBack


class MainActivity : AppCompatActivity(), ResultReceiverCallBack {
    val result: ResultReceiverCallBack = this
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        MyIntentService().startServiceForPython(this, "Suman", result)
    }

    override fun onSuccess(data: String) {
        Log.e("MainActivity", data.toString())
    }

    override fun onError(msg: String) {
        Log.e("MainActivity", msg)
    }
}