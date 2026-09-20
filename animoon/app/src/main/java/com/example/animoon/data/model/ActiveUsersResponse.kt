package com.example.animoon.data.model

data class ActiveUsersResponse(
    val status: String,
    val zonas: Map<String, List<ActiveUser>>
)

data class ActiveUser(
    val usuario_id: String,
    val nickname: String?,
    val x: Float?,
    val y: Float?
)
