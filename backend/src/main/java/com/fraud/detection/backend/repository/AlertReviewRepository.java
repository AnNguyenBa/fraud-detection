package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.AlertReview;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AlertReviewRepository
        extends JpaRepository<AlertReview, Long> {

    List<AlertReview> findByAlertIdOrderByReviewedAtDesc(Long alertId);

    List<AlertReview> findByReviewerId(Long reviewerId);
}