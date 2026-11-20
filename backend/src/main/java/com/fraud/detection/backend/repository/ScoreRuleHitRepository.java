package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.ScoreRuleHit;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ScoreRuleHitRepository
        extends JpaRepository<ScoreRuleHit, Long> {

    List<ScoreRuleHit> findByScoreId(Long scoreId);

    List<ScoreRuleHit> findByRuleCode(String ruleCode);
}