//package com.pega.moduledemo
//
//import android.os.Bundle
//import android.os.ResultReceiver
//import androidx.core.provider.FontsContractCompat.Columns.RESULT_CODE_OK
//
//
//class ResultReceiverImplementation<T> : ResultReceiver() {
//    //...
//    protected fun onReceiveResult(resultCode: Int, resultData: Bundle) {
//        if (mReceiver != null) {
//            if (resultCode == RESULT_CODE_OK) {
//                mReceiver.onSuccess(resultData.getSerializable(PARAM_RESULT))
//            } else {
//                mReceiver.onError(resultData.getSerializable(PARAM_EXCEPTION) as Exception?)
//            }
//        }
//    }
//}