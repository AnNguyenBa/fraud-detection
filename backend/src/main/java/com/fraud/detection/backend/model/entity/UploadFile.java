
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "UPLOAD_FILE")
@Getter
@Setter
@NoArgsConstructor
public class UploadFile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "FILE_NAME", length = 255, nullable = false)
    private String fileName;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "UPLOADED_BY", nullable = false)
    private AppUser uploadedBy;

    @Column(name = "STATUS", length = 20, nullable = false)
    private String status = "DANG_XU_LY";

    @Column(name = "TOTAL_ROWS", nullable = false)
    private Long totalRows = 0L;

    @Column(name = "VALID_ROWS", nullable = false)
    private Long validRows = 0L;

    @Column(name = "INVALID_ROWS", nullable = false)
    private Long invalidRows = 0L;

    @Column(name = "CREATED_AT", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "FINISHED_AT")
    private LocalDateTime finishedAt;
}
