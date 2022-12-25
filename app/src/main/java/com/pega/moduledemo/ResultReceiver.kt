package com.pega.moduledemo

interface ResultReceiverCallBack<T> {
    fun onSuccess(data: T)
    fun onError(exception: Exception?)
}