package com.example.animoon.data.model

data class NicknameCheckRequest(
    val nickname: String
)

data class SmsSendRequest(
    val nickname: String,
    val telefono: String
)

data class FinalRegisterRequest(
    val nickname: String,
    val telefono: String,
    val codigo_verificacion: String,
    val password: String,
    val avatar_especie: String,
    val avatar_color: String
)

data class DefaultResponse(
    val message: String,
    val status: String
)
