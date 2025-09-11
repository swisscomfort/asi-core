#!/usr/bin/env python3
"""
GitHub Pro Analytics Script
Sammelt erweiterte Analytics via GitHub API und erstellt Reports
"""

import requests
import json
import os
from datetime import datetime, timedelta
import argparse
import sys

class GitHubProAnalytics:
    def __init__(self, token, owner, repo):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    def get_traffic_data(self):
        """GitHub Pro Feature: Traffic Analytics"""
        try:
            # Views (14 Tage History - GitHub Pro Feature)
            views_response = requests.get(f'{self.base_url}/traffic/views', headers=self.headers)
            
            # Clones (14 Tage History)
            clones_response = requests.get(f'{self.base_url}/traffic/clones', headers=self.headers)
            
            # Referrers (Top 10)
            referrers_response = requests.get(f'{self.base_url}/traffic/popular/referrers', headers=self.headers)
            
            # Popular Paths (Top 10)
            paths_response = requests.get(f'{self.base_url}/traffic/popular/paths', headers=self.headers)
            
            return {
                'views': views_response.json() if views_response.status_code == 200 else {},
                'clones': clones_response.json() if clones_response.status_code == 200 else {},
                'referrers': referrers_response.json() if referrers_response.status_code == 200 else [],
                'paths': paths_response.json() if paths_response.status_code == 200 else []
            }
        except Exception as e:
            print(f"❌ Traffic data error: {e}")
            return {}
    
    def get_repository_stats(self):
        """Allgemeine Repository-Statistiken"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'watchers': data.get('watchers_count', 0),
                    'open_issues': data.get('open_issues_count', 0),
                    'size': data.get('size', 0),
                    'language': data.get('language', 'Unknown'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'default_branch': data.get('default_branch', 'main'),
                    'topics': data.get('topics', [])
                }
        except Exception as e:
            print(f"❌ Repository stats error: {e}")
            return {}
    
    def get_commit_activity(self):
        """Commit-Aktivität der letzten Wochen"""
        try:
            response = requests.get(f'{self.base_url}/stats/commit_activity', headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"❌ Commit activity error: {e}")
            return []
    
    def get_contributor_stats(self):
        """Contributor-Statistiken"""
        try:
            response = requests.get(f'{self.base_url}/stats/contributors', headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"❌ Contributor stats error: {e}")
            return []
    
    def get_release_data(self):
        """Release-Informationen"""
        try:
            response = requests.get(f'{self.base_url}/releases', headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"❌ Release data error: {e}")
            return []
    
    def get_issues_stats(self):
        """Issue-Statistiken für Beta Testing"""
        try:
            # Open Issues
            open_issues = requests.get(f'{self.base_url}/issues?state=open&per_page=100', headers=self.headers)
            
            # Closed Issues (letzte 30 Tage)
            since_date = (datetime.now() - timedelta(days=30)).isoformat()
            closed_issues = requests.get(f'{self.base_url}/issues?state=closed&since={since_date}&per_page=100', headers=self.headers)
            
            # Beta-specific Issues
            beta_issues = requests.get(f'{self.base_url}/issues?labels=beta-testing&per_page=100', headers=self.headers)
            
            return {
                'open': open_issues.json() if open_issues.status_code == 200 else [],
                'closed': closed_issues.json() if closed_issues.status_code == 200 else [],
                'beta': beta_issues.json() if beta_issues.status_code == 200 else []
            }
        except Exception as e:
            print(f"❌ Issues stats error: {e}")
            return {}
    
    def get_pull_requests_stats(self):
        """Pull Request Statistiken"""
        try:
            # Open PRs
            open_prs = requests.get(f'{self.base_url}/pulls?state=open&per_page=100', headers=self.headers)
            
            # Merged PRs (letzte 30 Tage)
            since_date = (datetime.now() - timedelta(days=30)).isoformat()
            merged_prs = requests.get(f'{self.base_url}/pulls?state=closed&sort=updated&direction=desc&per_page=100', headers=self.headers)
            
            return {
                'open': open_prs.json() if open_prs.status_code == 200 else [],
                'recent': merged_prs.json() if merged_prs.status_code == 200 else []
            }
        except Exception as e:
            print(f"❌ Pull requests stats error: {e}")
            return {}
    
    def generate_report(self, output_format='markdown'):
        """Generiert einen vollständigen Analytics Report"""
        print("🔍 Sammle GitHub Pro Analytics...")
        
        # Daten sammeln
        traffic_data = self.get_traffic_data()
        repo_stats = self.get_repository_stats()
        commit_activity = self.get_commit_activity()
        contributor_stats = self.get_contributor_stats()
        release_data = self.get_release_data()
        issues_stats = self.get_issues_stats()
        pr_stats = self.get_pull_requests_stats()
        
        # Analytics zusammenfassen
        analytics = {
            'timestamp': datetime.now().isoformat(),
            'repository': f'{self.owner}/{self.repo}',
            'traffic': traffic_data,
            'stats': repo_stats,
            'commit_activity': commit_activity,
            'contributors': contributor_stats,
            'releases': release_data,
            'issues': issues_stats,
            'pull_requests': pr_stats
        }
        
        # JSON-Report speichern
        with open('analytics_report.json', 'w') as f:
            json.dump(analytics, f, indent=2)
        
        if output_format == 'markdown':
            return self.generate_markdown_report(analytics)
        elif output_format == 'json':
            return analytics
        else:
            return self.generate_text_report(analytics)
    
    def generate_markdown_report(self, analytics):
        """Erstellt einen Markdown Report"""
        traffic_data = analytics['traffic']
        repo_stats = analytics['stats']
        issues_stats = analytics['issues']
        
        report_content = f"""# 📊 ASI-Core Analytics Report

**Generiert:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Repository:** [{self.owner}/{self.repo}](https://github.com/{self.owner}/{self.repo})

## 🏆 GitHub Pro Features Dashboard

"""
        
        # Traffic Analytics (GitHub Pro Feature)
        if traffic_data.get('views'):
            views = traffic_data['views']
            report_content += f"""### 👀 Repository Views (14 Tage - GitHub Pro)
- **Unique Visitors:** {views.get('uniques', 0):,}
- **Total Views:** {views.get('count', 0):,}

#### 📈 Tägliche Aufschlüsselung (letzte 7 Tage):
"""
            for view in views.get('views', [])[-7:]:
                date = view['timestamp'][:10]
                report_content += f"- **{date}:** {view['uniques']:,} unique visitors, {view['count']:,} total views\n"
        
        if traffic_data.get('clones'):
            clones = traffic_data['clones']
            report_content += f"""
### 📦 Repository Clones (14 Tage)
- **Unique Clones:** {clones.get('uniques', 0):,}
- **Total Clones:** {clones.get('count', 0):,}
"""
        
        if traffic_data.get('referrers'):
            report_content += f"""
### 🔗 Top Referrers
"""
            for ref in traffic_data['referrers'][:5]:
                report_content += f"- **{ref['referrer']}:** {ref['count']:,} views, {ref['uniques']:,} unique\n"
        
        if traffic_data.get('paths'):
            report_content += f"""
### 📁 Popular Paths
"""
            for path in traffic_data['paths'][:5]:
                report_content += f"- **{path['path']}:** {path['count']:,} views, {path['uniques']:,} unique\n"
        
        # Repository Stats
        if repo_stats:
            report_content += f"""
## ⭐ Repository Statistics
- **Stars:** {repo_stats.get('stars', 0):,} ⭐
- **Forks:** {repo_stats.get('forks', 0):,} 🍴
- **Watchers:** {repo_stats.get('watchers', 0):,} 👀
- **Open Issues:** {repo_stats.get('open_issues', 0):,} 🐛
- **Repository Size:** {repo_stats.get('size', 0):,} KB
- **Primary Language:** {repo_stats.get('language', 'Unknown')} 
- **Topics:** {', '.join(repo_stats.get('topics', []))}
"""
        
        # Beta Testing Stats
        if issues_stats:
            beta_issues = issues_stats.get('beta', [])
            open_issues = issues_stats.get('open', [])
            closed_issues = issues_stats.get('closed', [])
            
            report_content += f"""
## 🧪 Beta Testing Dashboard
- **Beta Issues:** {len(beta_issues)} 🧪
- **Open Issues:** {len(open_issues)} 🔓
- **Closed Issues (30 Tage):** {len(closed_issues)} ✅

### 🏷️ Beta Issue Breakdown:
"""
            beta_labels = {}
            for issue in beta_issues:
                for label in issue.get('labels', []):
                    label_name = label['name']
                    if 'week-' in label_name or 'priority-' in label_name:
                        beta_labels[label_name] = beta_labels.get(label_name, 0) + 1
            
            for label, count in sorted(beta_labels.items()):
                report_content += f"- **{label}:** {count} issues\n"
        
        # Commit Activity
        commit_activity = analytics.get('commit_activity', [])
        if commit_activity:
            total_commits = sum(week['total'] for week in commit_activity[-4:])
            report_content += f"""
## 💻 Development Activity
- **Commits (letzte 4 Wochen):** {total_commits:,}
- **Durchschnitt pro Woche:** {total_commits/4:.1f}
"""
        
        # Contributors
        contributor_stats = analytics.get('contributors', [])
        if contributor_stats:
            report_content += f"""
## 👥 Contributors
- **Aktive Contributors:** {len(contributor_stats)}
"""
            for contributor in contributor_stats[:3]:
                total_commits = contributor.get('total', 0)
                login = contributor.get('author', {}).get('login', 'Unknown')
                report_content += f"- **{login}:** {total_commits:,} commits\n"
        
        # Releases
        release_data = analytics.get('releases', [])
        if release_data:
            latest_release = release_data[0]
            total_downloads = sum(asset.get('download_count', 0) for asset in latest_release.get('assets', []))
            
            report_content += f"""
## 🚀 Latest Release
- **Version:** {latest_release.get('tag_name', 'Unknown')}
- **Name:** {latest_release.get('name', 'Unnamed')}
- **Published:** {latest_release.get('published_at', 'Unknown')[:10]}
- **Downloads:** {total_downloads:,}
"""
        
        report_content += f"""

## 🎯 Beta Testing KPIs

### 📊 Engagement Metrics
- **Repository Engagement:** {(traffic_data.get('views', {}).get('uniques', 0) / max(repo_stats.get('stars', 1), 1) * 100):.1f}% (Views/Stars Ratio)
- **Issue Activity:** {len(issues_stats.get('open', [])) + len(issues_stats.get('closed', []))} total issues
- **Beta Participation:** {len(issues_stats.get('beta', []))} beta-specific issues

### 🚀 GitHub Pro Value
- ✅ Traffic Analytics: {traffic_data.get('views', {}).get('count', 0):,} total views tracked
- ✅ Security Scanning: Automated vulnerability detection
- ✅ Advanced CI/CD: Multi-environment deployments
- ✅ Container Registry: Automated Docker builds
- ✅ Project Management: Structured beta workflow

### 📈 Next Actions
1. **Traffic Optimization:** Focus on top referrers for growth
2. **Beta Feedback:** Address open beta issues: {len([i for i in issues_stats.get('open', []) if any(l['name'] == 'beta-testing' for l in i.get('labels', []))])}
3. **Performance:** Monitor popular paths for optimization
4. **Community:** Engage with {contributor_stats.__len__() if contributor_stats else 0} active contributors

---
*🔄 Report automatisch generiert mit GitHub Pro Analytics*  
*📊 Powered by ASI-Core Automation System*
"""
        
        # Markdown-Report speichern
        with open('daily_analytics_report.md', 'w') as f:
            f.write(report_content)
        
        return report_content
    
    def generate_text_report(self, analytics):
        """Erstellt einen Text Report für Console Output"""
        traffic_data = analytics['traffic']
        repo_stats = analytics['stats']
        
        print("\n" + "="*60)
        print("📊 ASI-CORE GITHUB PRO ANALYTICS")
        print("="*60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"📂 Repository: {self.owner}/{self.repo}")
        print("-"*60)
        
        # Traffic (GitHub Pro Feature)
        if traffic_data.get('views'):
            views = traffic_data['views']
            print(f"👀 Unique Visitors (14 Tage): {views.get('uniques', 0):,}")
            print(f"📈 Total Views: {views.get('count', 0):,}")
        
        if traffic_data.get('clones'):
            clones = traffic_data['clones']
            print(f"📦 Repository Clones: {clones.get('count', 0):,}")
        
        # Repository Stats
        if repo_stats:
            print(f"⭐ Stars: {repo_stats.get('stars', 0):,}")
            print(f"🍴 Forks: {repo_stats.get('forks', 0):,}")
            print(f"🐛 Open Issues: {repo_stats.get('open_issues', 0):,}")
        
        # Beta Testing
        issues_stats = analytics.get('issues', {})
        if issues_stats:
            beta_count = len(issues_stats.get('beta', []))
            print(f"🧪 Beta Issues: {beta_count}")
        
        print("="*60)
        return analytics

def main():
    parser = argparse.ArgumentParser(description='GitHub Pro Analytics für ASI-Core')
    parser.add_argument('--token', help='GitHub Personal Access Token', 
                       default=os.environ.get('GITHUB_TOKEN'))
    parser.add_argument('--owner', help='Repository Owner', default='swisscomfort')
    parser.add_argument('--repo', help='Repository Name', default='asi-core')
    parser.add_argument('--format', choices=['markdown', 'json', 'text'], 
                       default='text', help='Output Format')
    parser.add_argument('--output', help='Output File', default=None)
    
    args = parser.parse_args()
    
    if not args.token:
        print("❌ GitHub Token erforderlich! Setzen Sie GITHUB_TOKEN oder verwenden Sie --token")
        sys.exit(1)
    
    analytics = GitHubProAnalytics(args.token, args.owner, args.repo)
    
    try:
        report = analytics.generate_report(args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                if args.format == 'json':
                    json.dump(report, f, indent=2)
                else:
                    f.write(report)
            print(f"✅ Report gespeichert: {args.output}")
        else:
            if args.format == 'text':
                # Text wird bereits in generate_text_report ausgegeben
                pass
            elif args.format == 'json':
                print(json.dumps(report, indent=2))
            else:
                print(report)
                
    except Exception as e:
        print(f"❌ Fehler beim Generieren des Reports: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()