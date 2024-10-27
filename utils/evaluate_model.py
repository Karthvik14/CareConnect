import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from datetime import datetime
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from textblob import TextBlob

class ModelEvaluator:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-002",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        self.results_dir = 'evaluation_results'
        self.plots_dir = 'evaluation_plots'
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.plots_dir, exist_ok=True)

    def evaluate_response_quality(self, response_text, expected_sections):
        quality_metrics = {
            'section_coverage': 0,
            'response_coherence': 0,
            'medical_relevance': 0,
            'practical_advice': 0
        }

        # Check section coverage
        sections_found = 0
        for section in expected_sections:
            if section.lower() in response_text.lower():
                sections_found += 1
        quality_metrics['section_coverage'] = (sections_found / len(expected_sections)) * 100

        # Check response coherence (based on paragraph structure)
        paragraphs = response_text.split('\n\n')
        if len(paragraphs) >= 4:  # Expecting at least 4 main sections
            quality_metrics['response_coherence'] = 100
        else:
            quality_metrics['response_coherence'] = (len(paragraphs) / 4) * 100

        # Check medical relevance (keywords)
        medical_keywords = ['symptoms', 'treatment', 'management', 'prevention', 'warning signs', 'relief']
        keywords_found = sum(1 for keyword in medical_keywords if keyword in response_text.lower())
        quality_metrics['medical_relevance'] = (keywords_found / len(medical_keywords)) * 100

        # Check practical advice
        practical_indicators = ['can', 'should', 'try', 'recommend', 'help', 'avoid']
        practical_count = sum(1 for indicator in practical_indicators if indicator in response_text.lower())
        quality_metrics['practical_advice'] = (practical_count / len(practical_indicators)) * 100

        return quality_metrics

    def evaluate_responses(self, test_cases):
        results = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'test_results': [],
            'average_metrics': {
                'response_time': [],
                'section_coverage': [],
                'response_coherence': [],
                'medical_relevance': [],
                'practical_advice': []
            }
        }

        for case in test_cases:
            try:
                print(f"\nEvaluating: {case['category']} - {case['input'][:50]}...")
                
                start_time = datetime.now()
                response = self.model.generate_content(case['input'])
                response_time = (datetime.now() - start_time).total_seconds()

                if response and hasattr(response, 'text'):
                    # Evaluate response quality
                    quality_metrics = self.evaluate_response_quality(
                        response.text,
                        case['expected_sections']
                    )

                    case_result = {
                        'category': case['category'],
                        'input': case['input'],
                        'response': response.text,
                        'response_time': response_time,
                        'quality_metrics': quality_metrics
                    }

                    # Update average metrics
                    results['average_metrics']['response_time'].append(response_time)
                    for metric, value in quality_metrics.items():
                        results['average_metrics'][metric].append(value)

                else:
                    case_result = {
                        'category': case['category'],
                        'input': case['input'],
                        'error': 'Failed to generate response'
                    }

                results['test_results'].append(case_result)
                
            except Exception as e:
                print(f"Error evaluating case: {str(e)}")
                results['test_results'].append({
                    'category': case['category'],
                    'input': case['input'],
                    'error': str(e)
                })

        # Calculate averages
        for metric in results['average_metrics']:
            values = results['average_metrics'][metric]
            results['average_metrics'][metric] = sum(values) / len(values) if values else 0

        self._generate_visualizations(results)
        self._save_results(results)
        return results

    def _generate_visualizations(self, results):
        # Prepare data for visualization
        categories = [result['category'] for result in results['test_results'] if 'quality_metrics' in result]
        metrics = ['section_coverage', 'response_coherence', 'medical_relevance', 'practical_advice']
        
        # Create metrics by category DataFrame
        data = []
        for category in set(categories):
            category_results = [r for r in results['test_results'] 
                              if 'category' in r and r['category'] == category and 'quality_metrics' in r]
            if category_results:
                metrics_avg = {metric: sum(r['quality_metrics'][metric] for r in category_results) / len(category_results)
                             for metric in metrics}
                metrics_avg['Category'] = category
                data.append(metrics_avg)
        
        df = pd.DataFrame(data)
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(df[metrics].T, annot=True, cmap='YlOrRd', 
                   xticklabels=df['Category'], yticklabels=metrics)
        plt.title('Response Quality Metrics by Category')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'quality_metrics_heatmap.png'))
        plt.close()

    def _save_results(self, results):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"evaluation_results_{timestamp}.json"
        with open(os.path.join(self.results_dir, filename), 'w') as f:
            json.dump(results, f, indent=4)

def main():
    from api_key import api_key

    # More comprehensive test cases
    test_cases = [
        {
            'category': 'Acute Symptoms',
            'input': "I've had a severe headache since this morning, with sensitivity to light and some nausea. What should I do?",
            'expected_sections': ['Greeting', 'Immediate Steps', 'Management', 'Warning Signs']
        },
        {
            'category': 'Chronic Condition',
            'input': "I've been experiencing lower back pain for the past month, especially when sitting for long hours. How can I manage this?",
            'expected_sections': ['Greeting', 'Assessment', 'Management', 'Prevention', 'Warning Signs']
        },
        {
            'category': 'Mental Health',
            'input': "I've been feeling anxious and having trouble sleeping lately due to work stress. What can help?",
            'expected_sections': ['Greeting', 'Understanding', 'Coping Strategies', 'Lifestyle Changes', 'Professional Help']
        },
        {
            'category': 'Emergency',
            'input': "I'm experiencing chest pain and shortness of breath. What should I do?",
            'expected_sections': ['Urgent Warning', 'Immediate Action', 'Emergency Signs']
        },
        {
            'category': 'Preventive Care',
            'input': "What are some effective ways to maintain good health while working from home?",
            'expected_sections': ['Greeting', 'Physical Health', 'Mental Health', 'Ergonomics', 'Routine']
        }
    ]

    evaluator = ModelEvaluator(api_key)
    results = evaluator.evaluate_responses(test_cases)

    print("\nEvaluation Summary:")
    print("\nAverage Metrics:")
    for metric, value in results['average_metrics'].items():
        print(f"{metric.replace('_', ' ').title()}: {value:.2f}")

    print("\nDetailed Results by Category:")
    for result in results['test_results']:
        if 'error' not in result:
            print(f"\nCategory: {result['category']}")
            print(f"Response Time: {result['response_time']:.2f}s")
            print("Quality Metrics:")
            for metric, value in result['quality_metrics'].items():
                print(f"- {metric.replace('_', ' ').title()}: {value:.2f}%")

if __name__ == "__main__":
    main()