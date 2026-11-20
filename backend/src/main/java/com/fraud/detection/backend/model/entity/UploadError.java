
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "UPLOAD_ERROR")
@Getter
@Setter
@NoArgsConstructor
public class UploadError {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "UPLOAD_ID", nullable = false)
    private UploadFile upload;

    @Column(name = "ROW_NUMBER", nullable = false)
    private Long rowNumber;

    @Column(name = "FIELD_NAME", length = 50)
    private String fieldName;

    @Column(name = "MESSAGE", length = 300, nullable = false)
    private String message;
}
