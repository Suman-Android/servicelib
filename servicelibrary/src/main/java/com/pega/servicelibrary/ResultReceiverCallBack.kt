package com.pega.servicelibrary;

interface ResultReceiverCallBack {
    fun onSuccess(data: String)
    fun onError(msg: String)
}