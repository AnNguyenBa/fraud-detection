
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(
        name = "TXN_SCORE",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "UQ_SCORE",
                        columnNames = {"TXN_ID", "MODEL_VERSION_ID"}
                )
        }
)
@Getter
@Setter
@NoArgsConstructor
public class TxnScore {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "TXN_ID", nullable = false)
    private Txn txn;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "MODEL_VERSION_ID", nullable = false)
    private ModelVersion modelVersion;

    @Column(name = "ANOMALY_SCORE", precision = 6, scale = 2, nullable = false)
    private BigDecimal anomalyScore;

    @Column(name = "FRAUD_PROBABILITY", precision = 6, scale = 2, nullable = false)
    private BigDecimal fraudProbability;

    @Column(name = "RULE_SCORE", precision = 6, scale = 2, nullable = false)
    private BigDecimal ruleScore;

    @Column(name = "FINAL_SCORE", precision = 6, scale = 2, nullable = false)
    private BigDecimal finalScore;

    @Column(name = "RISK_LEVEL", length = 10, nullable = false)
    private String riskLevel;

    @Lob
    @Column(name = "TOP_FEATURES")
    private String topFeatures;

    @Column(name = "SCORED_AT", nullable = false)
    private LocalDateTime scoredAt;
}
