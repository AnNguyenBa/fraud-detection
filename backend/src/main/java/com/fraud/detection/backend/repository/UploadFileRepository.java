package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.UploadFile;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UploadFileRepository
        extends JpaRepository<UploadFile, Long> {

    List<UploadFile> findByUploadedByOrderByCreatedAtDesc(Long uploadedBy);

    List<UploadFile> findByStatus(String status);
}