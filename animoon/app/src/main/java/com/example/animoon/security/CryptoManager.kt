package com.example.animoon.security

import org.bouncycastle.jce.provider.BouncyCastleProvider
import java.security.KeyFactory
import java.security.KeyPair
import java.security.KeyPairGenerator
import java.security.Security
import java.security.spec.X509EncodedKeySpec
import javax.crypto.KeyAgreement
import android.util.Base64
import java.security.MessageDigest
import javax.crypto.spec.SecretKeySpec
import javax.crypto.Mac

object CryptoManager {
    init {
        // Asegurar que BouncyCastle está registrado como proveedor de seguridad primario
        Security.removeProvider("BC")
        Security.addProvider(BouncyCastleProvider())
    }

    /**
     * Genera un par de llaves X25519 efímeras.
     */
    fun generateEphemeralKeyPair(): KeyPair {
        val kpg = KeyPairGenerator.getInstance("X25519", "BC")
        return kpg.generateKeyPair()
    }

    /**
     * Extrae los 32 bytes crudos de la llave pública X25519 y los codifica en Base64
     * para coincidir exactamente con el formato crudo que espera Python (cryptography).
     */
    fun getPublicKeyBase64(keyPair: KeyPair): String {
        // La llave pública en Java suele estar en formato X.509 (SubjectPublicKeyInfo).
        // En X25519, los últimos 32 bytes del arreglo codificado son la llave cruda.
        val encoded = keyPair.public.encoded
        val rawKey = encoded.copyOfRange(encoded.size - 32, encoded.size)
        return Base64.encodeToString(rawKey, Base64.NO_WRAP)
    }

    /**
     * Calcula el secreto compartido (Shared Secret) usando ECDHE.
     * Toma la llave privada generada localmente y la llave pública cruda del servidor en Base64.
     */
    fun computeSharedSecret(clientKeyPair: KeyPair, serverPublicKeyBase64: String): String {
        // Decodificar la llave pública cruda de 32 bytes
        val serverRawKey = Base64.decode(serverPublicKeyBase64, Base64.NO_WRAP)
        if (serverRawKey.size != 32) {
            throw IllegalArgumentException("La llave pública del servidor debe ser de 32 bytes")
        }

        // Construir el formato X.509 requerido por Java (Prefijo OID para X25519: 12 bytes)
        val prefix = byteArrayOf(
            0x30.toByte(), 0x2A.toByte(), 0x30.toByte(), 0x05.toByte(), 0x06.toByte(), 0x03.toByte(),
            0x2B.toByte(), 0x65.toByte(), 0x6E.toByte(), 0x03.toByte(), 0x21.toByte(), 0x00.toByte()
        )
        val x509Key = ByteArray(prefix.size + serverRawKey.size)
        System.arraycopy(prefix, 0, x509Key, 0, prefix.size)
        System.arraycopy(serverRawKey, 0, x509Key, prefix.size, serverRawKey.size)

        val keyFactory = KeyFactory.getInstance("X25519", "BC")
        val serverPublicKey = keyFactory.generatePublic(X509EncodedKeySpec(x509Key))

        // Intercambio matemático Diffie-Hellman
        val keyAgreement = KeyAgreement.getInstance("X25519", "BC")
        keyAgreement.init(clientKeyPair.private)
        keyAgreement.doPhase(serverPublicKey, true)
        val sharedSecret = keyAgreement.generateSecret()

        // Derivar llave AES-256 usando HKDF-SHA256 para empatar con Python
        val derivedKey = performHKDF(sharedSecret, "animoon-session-key".toByteArray())
        return Base64.encodeToString(derivedKey, Base64.NO_WRAP)
    }

    /**
     * Implementación básica de HKDF (HMAC-based Extract-and-Expand Key Derivation Function) RFC 5869
     * Extrae un secreto fuerte y lo expande a 32 bytes (256 bits).
     */
    private fun performHKDF(ikm: ByteArray, info: ByteArray): ByteArray {
        val mac = Mac.getInstance("HmacSHA256")
        // Extract (Salt = zeros if null)
        val salt = ByteArray(32) // 32 bytes of zeros
        mac.init(SecretKeySpec(salt, "HmacSHA256"))
        val prk = mac.doFinal(ikm)
        
        // Expand
        mac.init(SecretKeySpec(prk, "HmacSHA256"))
        mac.update(info)
        mac.update(byteArrayOf(0x01)) // counter
        val expanded = mac.doFinal()
        return expanded.copyOfRange(0, 32)
    }
}
