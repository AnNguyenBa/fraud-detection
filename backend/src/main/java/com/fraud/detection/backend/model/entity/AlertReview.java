
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "ALERT_REVIEW")
@Getter
@Setter
@NoArgsConstructor
public class AlertReview {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ALERT_ID", nullable = false)
    private Alert alert;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "REVIEWER_ID", nullable = false)
    private AppUser reviewer;

    @Column(name = "VERDICT", length = 15, nullable = false)
    private String verdict;

    @Column(name = "NOTE", length = 1000)
    private String note;

    @Column(name = "REVIEWED_AT", nullable = false)
    private LocalDateTime reviewedAt;
}
