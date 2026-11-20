
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "MODEL_VERSION",
        uniqueConstraints = {
                @UniqueConstraint(name = "UQ_MODEL_VERSION", columnNames = "VERSION")
        }
)
@Getter
@Setter
@NoArgsConstructor
public class ModelVersion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "VERSION", length = 50, nullable = false)
    private String version;

    @Column(name = "TRAINED_AT")
    private LocalDateTime trainedAt;

    @Column(name = "NOTES", length = 500)
    private String notes;
}
