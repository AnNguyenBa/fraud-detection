package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.Alert;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface AlertRepository extends JpaRepository<Alert, Long> {

    Optional<Alert> findByScoreId(Long scoreId);

    List<Alert> findByStatusOrderByCreatedAtDesc(String status);

    List<Alert> findAllByOrderByCreatedAtDesc();
}