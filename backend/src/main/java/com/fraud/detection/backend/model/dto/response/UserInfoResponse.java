package com.fraud.detection.backend.model.dto.response;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class UserInfoResponse {

    private Long id;
    private String username;
    private String role;
}