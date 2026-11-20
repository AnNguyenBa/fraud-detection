package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.UploadError;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UploadErrorRepository
        extends JpaRepository<UploadError, Long> {

    List<UploadError> findByUploadIdOrderByRowNumberAsc(Long uploadId);

    long countByUploadId(Long uploadId);
}