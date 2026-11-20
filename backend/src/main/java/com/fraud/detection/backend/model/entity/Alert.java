
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "ALERT",
        uniqueConstraints = {@UniqueConstraint(name = "UQ_ALERT_SCORE", columnNames = "SCORE_ID")
        }
)
@Getter
@Setter
@NoArgsConstructor
public class Alert {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "SCORE_ID", nullable = false)
    private TxnScore score;

    @Column(name = "STATUS", length = 15, nullable = false)
    private String status = "MOI";

    @Column(name = "CREATED_AT", nullable = false)
    private LocalDateTime createdAt;
}
