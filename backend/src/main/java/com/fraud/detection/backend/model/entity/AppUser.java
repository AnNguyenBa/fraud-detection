
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "APP_USER",
        uniqueConstraints = {
                @UniqueConstraint(name = "UQ_APP_USER_USERNAME", columnNames = "USERNAME")
        }
)
@Getter
@Setter
@NoArgsConstructor
public class AppUser {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "USERNAME", length = 50, nullable = false)
    private String username;

    @Column(name = "PASSWORD_HASH", length = 100, nullable = false)
    private String passwordHash;

    @Column(name = "ROLE", length = 20, nullable = false)
    private String role;

    @Column(name = "ENABLED", nullable = false)
    private Integer enabled = 1;

    @Column(name = "CREATED_AT", nullable = false)
    private LocalDateTime createdAt;
}
