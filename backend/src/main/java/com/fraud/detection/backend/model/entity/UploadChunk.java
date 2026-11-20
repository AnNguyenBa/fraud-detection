
package com.fraud.detection.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

@Entity
@Table(
        name = "UPLOAD_CHUNK",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "UQ_CHUNK",
                        columnNames = {"UPLOAD_ID", "CHUNK_NO"}
                )
        }
)
@Getter
@Setter
@NoArgsConstructor
public class UploadChunk {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "UPLOAD_ID", nullable = false)
    private UploadFile upload;

    @Column(name = "CHUNK_NO", nullable = false)
    private Integer chunkNo;

    @Column(name = "ROW_FROM", nullable = false)
    private Long rowFrom;

    @Column(name = "ROW_TO", nullable = false)
    private Long rowTo;

    @Column(name = "STATUS", length = 20, nullable = false)
    private String status = "CHO_XU_LY";

    @Column(name = "ERROR_MESSAGE", length = 500)
    private String errorMessage;
}
