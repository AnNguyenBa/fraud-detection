package com.fraud.detection.backend.repository;

import com.fraud.detection.backend.model.entity.Txn;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface TxnRepository extends JpaRepository<Txn, Long> {

    List<Txn> findByUploadId(Long uploadId);

    List<Txn> findByStatus(String status);

    long countByUploadId(Long uploadId);
}