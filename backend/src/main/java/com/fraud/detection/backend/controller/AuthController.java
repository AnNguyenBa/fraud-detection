package com.fraud.detection.backend.controller;

import com.fraud.detection.backend.model.dto.request.LoginRequest;
import com.fraud.detection.backend.model.dto.response.AuthResponse;
import com.fraud.detection.backend.model.dto.response.UserInfoResponse;
import com.fraud.detection.backend.security.UserPrincipal;
import com.fraud.detection.backend.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public AuthResponse login(@Valid @RequestBody LoginRequest request) {
        return authService.login(request);
    }

    @GetMapping("/me")
    public UserInfoResponse getCurrentUser(
            @AuthenticationPrincipal UserPrincipal user
    ) {
        return new UserInfoResponse(
                user.getId(),
                user.getUsername(),
                user.getRole()
        );
    }
}