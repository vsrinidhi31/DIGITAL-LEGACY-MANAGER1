package com.example.aes.service;
 
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
 
public class AESService {
 
    private static final String KEY = "1234567890123456";
 
    public static byte[] encrypt(byte[] data) throws Exception {
        SecretKeySpec key = new SecretKeySpec(KEY.getBytes(), "AES");
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        return cipher.doFinal(data);
    }
 
    public static byte[] decrypt(byte[] data) throws Exception {
        SecretKeySpec key = new SecretKeySpec(KEY.getBytes(), "AES");
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.DECRYPT_MODE, key);
        return cipher.doFinal(data);
    }
 
    public static String encryptFileName(String fileName) throws Exception {
        return Base64.getUrlEncoder().encodeToString(encrypt(fileName.getBytes()));
    }
 
    public static String decryptFileName(String fileName) throws Exception {
        return new String(decrypt(Base64.getUrlDecoder().decode(fileName)));
    }
}
 



