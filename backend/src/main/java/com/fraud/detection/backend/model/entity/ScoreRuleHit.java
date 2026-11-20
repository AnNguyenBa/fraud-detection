
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Entity
@Table(name = "SCORE_RULE_HIT")
@Getter
@Setter
@NoArgsConstructor
public class ScoreRuleHit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "SCORE_ID", nullable = false)
    private TxnScore score;

    @Column(name = "RULE_CODE", length = 50, nullable = false)
    private String ruleCode;

    @Column(name = "POINTS", precision = 6, scale = 2, nullable = false)
    private BigDecimal points;

    @Column(name = "DETAIL", length = 300)
    private String detail;
}
