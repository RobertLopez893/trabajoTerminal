package com.example.animoon.data.model

data class NicknameCheckRequest(
    val nickname: String
)

data class LoginRequest(
    val nickname: String,
    val password: String,
    val client_ecdhe_public_key: String
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

data class TokenResponse(
    val access_token: String,
    val token_type: String,
    val message: String,
    val status: String,
    val server_ecdhe_public_key: String? = null
)
