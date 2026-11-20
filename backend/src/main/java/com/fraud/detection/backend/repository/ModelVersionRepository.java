package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.ModelVersion;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ModelVersionRepository
        extends JpaRepository<ModelVersion, Long> {

    Optional<ModelVersion> findByVersion(String version);

    boolean existsByVersion(String version);
}