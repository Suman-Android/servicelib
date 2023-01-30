package com.pega.servicelibrary.utils;

import android.util.Log;

object Logger {
    private const val showLog = false;

    fun showErrorLog(tag: String="Logger", msg: String="") {
        if (showLog)
            Log.e(tag, msg)
    }
}
