
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "TXN")
@Getter
@Setter
@NoArgsConstructor
public class Txn {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "UPLOAD_ID")
    private UploadFile upload;

    @Column(name = "SOURCE", length = 10, nullable = false)
    private String source;

    @Column(name = "TIME_SEC", nullable = false)
    private Long timeSec;

    @Column(name = "AMOUNT", precision = 14, scale = 2, nullable = false)
    private BigDecimal amount;

    @Column(name = "V1")
    private Double v1;

    @Column(name = "V2")
    private Double v2;

    @Column(name = "V3")
    private Double v3;

    @Column(name = "V4")
    private Double v4;

    @Column(name = "V5")
    private Double v5;

    @Column(name = "V6")
    private Double v6;

    @Column(name = "V7")
    private Double v7;

    @Column(name = "V8")
    private Double v8;

    @Column(name = "V9")
    private Double v9;

    @Column(name = "V10")
    private Double v10;

    @Column(name = "V11")
    private Double v11;

    @Column(name = "V12")
    private Double v12;

    @Column(name = "V13")
    private Double v13;

    @Column(name = "V14")
    private Double v14;

    @Column(name = "V15")
    private Double v15;

    @Column(name = "V16")
    private Double v16;

    @Column(name = "V17")
    private Double v17;

    @Column(name = "V18")
    private Double v18;

    @Column(name = "V19")
    private Double v19;

    @Column(name = "V20")
    private Double v20;

    @Column(name = "V21")
    private Double v21;

    @Column(name = "V22")
    private Double v22;

    @Column(name = "V23")
    private Double v23;

    @Column(name = "V24")
    private Double v24;

    @Column(name = "V25")
    private Double v25;

    @Column(name = "V26")
    private Double v26;

    @Column(name = "V27")
    private Double v27;

    @Column(name = "V28")
    private Double v28;

    @Column(name = "CLASS_LABEL")
    private Integer classLabel;

    @Column(name = "STATUS", length = 10, nullable = false)
    private String status = "CHO_CHAM";

    @Column(name = "CREATED_AT", nullable = false)
    private LocalDateTime createdAt;
}
