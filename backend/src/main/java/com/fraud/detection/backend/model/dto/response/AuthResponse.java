package com.fraud.detection.backend.model.dto.response;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class AuthResponse {

    private String accessToken;
    private String tokenType;
    private long expiresIn;
    private Long userId;
    private String username;
    private String role;
}