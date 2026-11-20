package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.TxnScore;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface TxnScoreRepository
        extends JpaRepository<TxnScore, Long> {

    Optional<TxnScore> findByTxnIdAndModelVersionId(
            Long txnId,
            Long modelVersionId
    );

    List<TxnScore> findByModelVersionId(Long modelVersionId);

    List<TxnScore> findByRiskLevel(String riskLevel);
}