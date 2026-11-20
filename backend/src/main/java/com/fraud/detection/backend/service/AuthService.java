package com.fraud.detection.backend.service;

import com.fraud.detection.backend.model.dto.request.LoginRequest;
import com.fraud.detection.backend.model.dto.response.AuthResponse;
import com.fraud.detection.backend.model.entity.AppUser;
import com.fraud.detection.backend.repository.AppUserRepository;
import com.fraud.detection.backend.security.JwtService;
import com.fraud.detection.backend.security.UserPrincipal;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AppUserRepository appUserRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    @Value("${app.jwt.expiration}")
    private long expiration;

    public AuthResponse login(LoginRequest request) {

        AppUser user = appUserRepository.findByUsername(request.getUsername())
                .orElseThrow(() ->
                        new BadCredentialsException("Username hoặc password không đúng")
                );

        if (user.getEnabled() == null || user.getEnabled() != 1) {
            throw new BadCredentialsException("Tài khoản đã bị vô hiệu hóa");
        }

        if (!passwordEncoder.matches(
                request.getPassword(),
                user.getPasswordHash()
        )) {
            throw new BadCredentialsException("Username hoặc password không đúng");
        }

        UserPrincipal userPrincipal = new UserPrincipal(user);

        String token = jwtService.generateToken(userPrincipal);

        return new AuthResponse(
                token,
                "Bearer",
                expiration / 1000,
                user.getId(),
                user.getUsername(),
                user.getRole()
        );
    }
}