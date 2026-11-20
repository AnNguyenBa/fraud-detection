package com.fraud.detection.backend.common;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class PasswordGenerator {

    public static void main(String[] args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

        String passwordHash = encoder.encode("123456");

        System.out.println("BCrypt Hash: " + passwordHash);
    }
}