package com.example.animoon.security

import android.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec
import java.security.SecureRandom

object AESGCMCipher {
    // LLAVE MAESTRA COMPARTIDA CON EL BACKEND (solo para el prototipo/desarrollo)
    private const val HEX_KEY = "825fafe94b06cb4741126a928e43cd92d46c5e122257da849a631f606a04ca2b"
    private const val TAG_LENGTH_BIT = 128
    private const val NONCE_LENGTH_BYTE = 12

    private val secretKey: SecretKeySpec by lazy {
        val keyBytes = hexStringToByteArray(HEX_KEY)
        SecretKeySpec(keyBytes, "AES")
    }

    data class EncryptedData(
        val ciphertextB64: String,
        val nonceB64: String,
        val tagB64: String
    )

    fun encrypt(plaintext: String): EncryptedData {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val nonce = ByteArray(NONCE_LENGTH_BYTE)
        SecureRandom().nextBytes(nonce)
        val parameterSpec = GCMParameterSpec(TAG_LENGTH_BIT, nonce)

        cipher.init(Cipher.ENCRYPT_MODE, secretKey, parameterSpec)
        val cipherTextWithTag = cipher.doFinal(plaintext.toByteArray(Charsets.UTF_8))

        // En Java, AES/GCM concatena el ciphertext y el tag automǭticamente al final.
        // El tag siempre son los ǧltimos 16 bytes (128 bits).
        val cipherTextLength = cipherTextWithTag.size - (TAG_LENGTH_BIT / 8)
        val ciphertext = cipherTextWithTag.copyOfRange(0, cipherTextLength)
        val tag = cipherTextWithTag.copyOfRange(cipherTextLength, cipherTextWithTag.size)

        return EncryptedData(
            ciphertextB64 = Base64.encodeToString(ciphertext, Base64.NO_WRAP),
            nonceB64 = Base64.encodeToString(nonce, Base64.NO_WRAP),
            tagB64 = Base64.encodeToString(tag, Base64.NO_WRAP)
        )
    }

    fun decrypt(ciphertextB64: String, nonceB64: String, tagB64: String): String {
        val ciphertext = Base64.decode(ciphertextB64, Base64.NO_WRAP)
        val nonce = Base64.decode(nonceB64, Base64.NO_WRAP)
        val tag = Base64.decode(tagB64, Base64.NO_WRAP)

        // Concatenar ciphertext y tag para que Java pueda descifrarlo en GCM
        val cipherTextWithTag = ciphertext + tag

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val parameterSpec = GCMParameterSpec(TAG_LENGTH_BIT, nonce)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, parameterSpec)

        val plaintextBytes = cipher.doFinal(cipherTextWithTag)
        return String(plaintextBytes, Charsets.UTF_8)
    }

    private fun hexStringToByteArray(s: String): ByteArray {
        val len = s.length
        val data = ByteArray(len / 2)
        var i = 0
        while (i < len) {
            data[i / 2] = ((Character.digit(s[i], 16) shl 4) + Character.digit(s[i + 1], 16)).toByte()
            i += 2
        }
        return data
    }
}
