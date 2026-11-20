package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.UploadChunk;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface UploadChunkRepository
        extends JpaRepository<UploadChunk, Long> {

    List<UploadChunk> findByUploadIdOrderByChunkNoAsc(Long uploadId);

    Optional<UploadChunk> findByUploadIdAndChunkNo(
            Long uploadId,
            Integer chunkNo
    );
}