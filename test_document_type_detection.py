#!/usr/bin/env python3
"""
Test script to verify document type detection functionality
"""

from services.document_processor import DocumentProcessor

def test_document_type_detection():
    """Test automatic document type detection"""
    
    processor = DocumentProcessor()
    
    print("🧪 Testing Document Type Detection")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "filename": "insurance_policy.pdf",
            "content": "This insurance policy covers medical expenses up to $50,000. The premium is $200 per month. Deductible is $500. Claims must be filed within 30 days.",
            "expected": "Policy Wordings"
        },
        {
            "filename": "contract_agreement.docx",
            "content": "This agreement is entered into between Party A and Party B. The terms and conditions include liability clauses and termination rights. Jurisdiction is in New York.",
            "expected": "Legal Documents"
        },
        {
            "filename": "financial_report.pdf",
            "content": "Revenue for Q4 was $1.2M. Net profit increased by 15%. Assets totaled $5M. Cash flow was positive. Audit completed successfully.",
            "expected": "Financial Documents"
        },
        {
            "filename": "technical_spec.pdf",
            "content": "System architecture requires API integration. Database schema includes user tables. Implementation uses Python framework. Testing protocol established.",
            "expected": "Technical Documents"
        },
        {
            "filename": "medical_record.pdf",
            "content": "Patient diagnosed with hypertension. Treatment includes medication. Doctor prescribed ACE inhibitors. Recovery prognosis is good.",
            "expected": "Medical Documents"
        },
        {
            "filename": "random_document.txt",
            "content": "This is just some random text without specific keywords.",
            "expected": "unknown"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        detected_type = processor.detect_document_type(test_case["content"], test_case["filename"])
        status = "✅" if detected_type == test_case["expected"] else "❌"
        
        print(f"\n{i}. {test_case['filename']}")
        print(f"   Expected: {test_case['expected']}")
        print(f"   Detected: {detected_type}")
        print(f"   Status: {status}")
    
    print("\n" + "=" * 50)
    print("🎯 Document Type Detection Test Completed!")

if __name__ == "__main__":
    test_document_type_detection()
