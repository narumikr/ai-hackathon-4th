# インフラアーキテクチャ設計書 - Historical Travel Agent

## 概要

歴史学習特化型旅行AIエージェントシステムの本格運用を想定したGoogle Cloud Platformアーキテクチャ設計書。

## システム全体アーキテクチャ

### Draw.io用XML（システム全体図）

```xml
<mxfile host="app.diagrams.net" modified="2024-01-20T00:00:00.000Z" agent="5.0" etag="xxx" version="22.1.16">
  <diagram name="GCP Architecture" id="gcp-architecture">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- Internet/Users -->
        <mxCell id="users" value="Users&#xa;(Web Browser)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#232F3E;fillColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.users;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="60" height="60" />
        </mxCell>
        
        <!-- Google Cloud Platform -->
        <mxCell id="gcp-boundary" value="Google Cloud Platform" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;dashed=1;dashPattern=5 5;fontSize=16;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="200" y="20" width="900" height="760" />
        </mxCell>
        
        <!-- Frontend Layer -->
        <mxCell id="frontend-layer" value="Frontend Layer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="220" y="60" width="260" height="120" />
        </mxCell>
        
        <mxCell id="firebase-hosting" value="Firebase Hosting&#xa;(Next.js Static Site)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.cloudfront;" vertex="1" parent="1">
          <mxGeometry x="250" y="100" width="60" height="60" />
        </mxCell>
        
        <mxCell id="cdn" value="Cloud CDN" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.cloudfront_edge_location;" vertex="1" parent="1">
          <mxGeometry x="380" y="100" width="60" height="60" />
        </mxCell>
        
        <!-- Backend Layer -->
        <mxCell id="backend-layer" value="Backend Layer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="520" y="60" width="260" height="180" />
        </mxCell>
        
        <mxCell id="cloud-run" value="Cloud Run&#xa;(FastAPI)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.fargate;" vertex="1" parent="1">
          <mxGeometry x="550" y="100" width="60" height="60" />
        </mxCell>
        
        <mxCell id="load-balancer" value="Cloud Load&#xa;Balancing" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.application_load_balancer;" vertex="1" parent="1">
          <mxGeometry x="680" y="100" width="60" height="60" />
        </mxCell>
        
        <mxCell id="cloud-build" value="Cloud Build&#xa;(CI/CD)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.codebuild;" vertex="1" parent="1">
          <mxGeometry x="550" y="180" width="60" height="60" />
        </mxCell>
        
        <mxCell id="artifact-registry" value="Artifact Registry&#xa;(Container Images)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.ecr;" vertex="1" parent="1">
          <mxGeometry x="680" y="180" width="60" height="60" />
        </mxCell>
        
        <!-- AI/ML Layer -->
        <mxCell id="ai-layer" value="AI/ML Layer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="820" y="60" width="260" height="180" />
        </mxCell>
        
        <mxCell id="vertex-ai" value="Vertex AI&#xa;(Gemini)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.sagemaker;" vertex="1" parent="1">
          <mxGeometry x="850" y="100" width="60" height="60" />
        </mxCell>
        
        <mxCell id="vertex-search" value="Vertex AI&#xa;Search" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.elasticsearch_service;" vertex="1" parent="1">
          <mxGeometry x="980" y="100" width="60" height="60" />
        </mxCell>
        
        <mxCell id="gemini-tools" value="Gemini Built-in Tools&#xa;(Search, Maps, Vision)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1">
          <mxGeometry x="850" y="180" width="190" height="40" />
        </mxCell>
        
        <!-- Data Layer -->
        <mxCell id="data-layer" value="Data Layer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="220" y="280" width="860" height="180" />
        </mxCell>
        
        <mxCell id="cloud-sql" value="Cloud SQL&#xa;(PostgreSQL)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.rds;" vertex="1" parent="1">
          <mxGeometry x="280" y="320" width="60" height="60" />
        </mxCell>
        
        <mxCell id="memorystore" value="Memorystore&#xa;(Redis)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.elasticache;" vertex="1" parent="1">
          <mxGeometry x="420" y="320" width="60" height="60" />
        </mxCell>
        
        <mxCell id="cloud-storage" value="Cloud Storage&#xa;(Images)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.s3;" vertex="1" parent="1">
          <mxGeometry x="560" y="320" width="60" height="60" />
        </mxCell>
        
        <mxCell id="backup-storage" value="Cloud Storage&#xa;(Backups)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.s3_glacier;" vertex="1" parent="1">
          <mxGeometry x="700" y="320" width="60" height="60" />
        </mxCell>
        
        <!-- Security Layer -->
        <mxCell id="security-layer" value="Security &amp; Identity Layer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="220" y="500" width="860" height="120" />
        </mxCell>
        
        <mxCell id="iam" value="Identity &amp; Access&#xa;Management (IAM)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.iam;" vertex="1" parent="1">
          <mxGeometry x="280" y="540" width="60" height="60" />
        </mxCell>
        
        <mxCell id="secret-manager" value="Secret Manager" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.secrets_manager;" vertex="1" parent="1">
          <mxGeometry x="420" y="540" width="60" height="60" />
        </mxCell>
        
        <mxCell id="firebase-auth" value="Firebase&#xa;Authentication" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.cognito;" vertex="1" parent="1">
          <mxGeometry x="560" y="540" width="60" height="60" />
        </mxCell>
        
        <!-- Monitoring Layer -->
        <mxCell id="monitoring-layer" value="Monitoring &amp; Logging Layer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="220" y="660" width="860" height="100" />
        </mxCell>
        
        <mxCell id="cloud-monitoring" value="Cloud Monitoring" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.cloudwatch;" vertex="1" parent="1">
          <mxGeometry x="280" y="690" width="60" height="60" />
        </mxCell>
        
        <mxCell id="cloud-logging" value="Cloud Logging" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.cloudtrail;" vertex="1" parent="1">
          <mxGeometry x="420" y="690" width="60" height="60" />
        </mxCell>
        
        <mxCell id="error-reporting" value="Error Reporting" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.x_ray;" vertex="1" parent="1">
          <mxGeometry x="560" y="690" width="60" height="60" />
        </mxCell>
        
        <!-- Connections -->
        <!-- Users to Firebase Hosting (static content) -->
        <mxCell id="conn1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#82b366;" edge="1" parent="1" source="users" target="firebase-hosting">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Users to Load Balancer (API calls) -->
        <mxCell id="conn2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;" edge="1" parent="1" source="users" target="load-balancer">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Load Balancer to Cloud Run -->
        <mxCell id="conn2b" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;" edge="1" parent="1" source="load-balancer" target="cloud-run">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Backend to AI Services -->
        <mxCell id="conn3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#b85450;" edge="1" parent="1" source="cloud-run" target="vertex-ai">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Backend to Database -->
        <mxCell id="conn4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;" edge="1" parent="1" source="cloud-run" target="cloud-sql">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Backend to Cache -->
        <mxCell id="conn5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#9673a6;" edge="1" parent="1" source="cloud-run" target="memorystore">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Backend to Storage -->
        <mxCell id="conn6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d79b00;" edge="1" parent="1" source="cloud-run" target="cloud-storage">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## ネットワーク構成図

### Draw.io用XML（ネットワーク詳細）

```xml
<mxfile host="app.diagrams.net" modified="2024-01-20T00:00:00.000Z" agent="5.0" etag="yyy" version="22.1.16">
  <diagram name="Network Architecture" id="network-architecture">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- Internet -->
        <mxCell id="internet" value="Internet" style="ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=16;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="120" height="80" />
        </mxCell>
        
        <!-- Google Cloud Platform -->
        <mxCell id="gcp-network" value="Google Cloud Platform - asia-northeast1 (Tokyo)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;dashed=1;dashPattern=5 5;fontSize=16;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="280" y="20" width="800" height="700" />
        </mxCell>
        
        <!-- VPC Network -->
        <mxCell id="vpc" value="VPC Network: historical-travel-vpc" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="320" y="60" width="720" height="620" />
        </mxCell>
        
        <!-- Public Subnet -->
        <mxCell id="public-subnet" value="Public Subnet: 10.0.1.0/24" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="360" y="100" width="320" height="200" />
        </mxCell>
        
        <!-- Private Subnet -->
        <mxCell id="private-subnet" value="Private Subnet: 10.0.2.0/24" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="720" y="100" width="280" height="200" />
        </mxCell>
        
        <!-- Load Balancer -->
        <mxCell id="lb" value="Cloud Load Balancer&#xa;(Global HTTPS)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.application_load_balancer;" vertex="1" parent="1">
          <mxGeometry x="400" y="140" width="50" height="50" />
        </mxCell>
        
        <!-- Cloud Run -->
        <mxCell id="run1" value="Cloud Run&#xa;Instance 1" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.fargate;" vertex="1" parent="1">
          <mxGeometry x="500" y="140" width="50" height="50" />
        </mxCell>
        
        <mxCell id="run2" value="Cloud Run&#xa;Instance 2" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.fargate;" vertex="1" parent="1">
          <mxGeometry x="580" y="140" width="50" height="50" />
        </mxCell>
        
        <!-- NAT Gateway -->
        <mxCell id="nat" value="Cloud NAT" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.nat_gateway;" vertex="1" parent="1">
          <mxGeometry x="400" y="220" width="50" height="50" />
        </mxCell>
        
        <!-- Database -->
        <mxCell id="db-primary" value="Cloud SQL&#xa;Primary" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.rds;" vertex="1" parent="1">
          <mxGeometry x="760" y="140" width="50" height="50" />
        </mxCell>
        
        <mxCell id="db-replica" value="Cloud SQL&#xa;Read Replica" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.rds;" vertex="1" parent="1">
          <mxGeometry x="860" y="140" width="50" height="50" />
        </mxCell>
        
        <!-- Redis -->
        <mxCell id="redis" value="Memorystore&#xa;Redis" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.elasticache;" vertex="1" parent="1">
          <mxGeometry x="760" y="220" width="50" height="50" />
        </mxCell>
        
        <!-- Managed Services (Outside VPC) -->
        <mxCell id="managed-services" value="Managed Services (No VPC)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=12;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="360" y="340" width="640" height="320" />
        </mxCell>
        
        <!-- Firebase Hosting -->
        <mxCell id="firebase" value="Firebase Hosting&#xa;(Global CDN)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.cloudfront;" vertex="1" parent="1">
          <mxGeometry x="400" y="380" width="50" height="50" />
        </mxCell>
        
        <!-- Vertex AI -->
        <mxCell id="vertex" value="Vertex AI&#xa;(Gemini)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.sagemaker;" vertex="1" parent="1">
          <mxGeometry x="520" y="380" width="50" height="50" />
        </mxCell>
        
        <!-- Cloud Storage -->
        <mxCell id="storage" value="Cloud Storage&#xa;(Multi-Region)" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.s3;" vertex="1" parent="1">
          <mxGeometry x="640" y="380" width="50" height="50" />
        </mxCell>
        
        <!-- IAM -->
        <mxCell id="iam-net" value="IAM &amp; Security" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.iam;" vertex="1" parent="1">
          <mxGeometry x="760" y="380" width="50" height="50" />
        </mxCell>
        
        <!-- Monitoring -->
        <mxCell id="monitoring" value="Cloud Monitoring&#xa;&amp; Logging" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#FF9900;fillColor=#FF9900;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.cloudwatch;" vertex="1" parent="1">
          <mxGeometry x="880" y="380" width="50" height="50" />
        </mxCell>
        
        <!-- Security Groups -->
        <mxCell id="sg-web" value="Security Group: Web&#xa;- HTTP/HTTPS (80,443)&#xa;- From: 0.0.0.0/0" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="400" y="480" width="140" height="60" />
        </mxCell>
        
        <mxCell id="sg-app" value="Security Group: App&#xa;- HTTP (8080)&#xa;- From: Web SG only" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="580" y="480" width="140" height="60" />
        </mxCell>
        
        <mxCell id="sg-db" value="Security Group: DB&#xa;- PostgreSQL (5432)&#xa;- Redis (6379)&#xa;- From: App SG only" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="760" y="480" width="140" height="80" />
        </mxCell>
        
        <!-- Network Flow -->
        <!-- Users to Firebase Hosting (static content) -->
        <mxCell id="flow1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#82b366;startArrow=none;startFill=0;endArrow=classic;endFill=1;" edge="1" parent="1" source="internet" target="firebase">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Users to Load Balancer (API calls) -->
        <mxCell id="flow2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;" edge="1" parent="1" source="internet" target="lb">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;" edge="1" parent="1" source="lb" target="run1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;" edge="1" parent="1" source="lb" target="run2">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;" edge="1" parent="1" source="run1" target="db-primary">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;" edge="1" parent="1" source="run2" target="redis">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## データフロー図

### Draw.io用XML（データフロー）

```xml
<mxfile host="app.diagrams.net" modified="2024-01-20T00:00:00.000Z" agent="5.0" etag="zzz" version="22.1.16">
  <diagram name="Data Flow" id="data-flow">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- User -->
        <mxCell id="user-df" value="User" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="80" y="200" width="30" height="60" />
        </mxCell>
        
        <!-- Frontend -->
        <mxCell id="frontend-df" value="Next.js Frontend&#xa;(Firebase Hosting)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="200" y="200" width="120" height="60" />
        </mxCell>
        
        <!-- API Gateway -->
        <mxCell id="api-df" value="FastAPI Backend&#xa;(Cloud Run)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="400" y="200" width="120" height="60" />
        </mxCell>
        
        <!-- AI Service -->
        <mxCell id="ai-df" value="Vertex AI&#xa;(Gemini)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="600" y="120" width="120" height="60" />
        </mxCell>
        
        <!-- Database -->
        <mxCell id="db-df" value="Cloud SQL&#xa;(PostgreSQL)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="600" y="200" width="120" height="60" />
        </mxCell>
        
        <!-- Cache -->
        <mxCell id="cache-df" value="Memorystore&#xa;(Redis)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="1">
          <mxGeometry x="600" y="280" width="120" height="60" />
        </mxCell>
        
        <!-- Storage -->
        <mxCell id="storage-df" value="Cloud Storage&#xa;(Images)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1">
          <mxGeometry x="600" y="360" width="120" height="60" />
        </mxCell>
        
        <!-- External APIs -->
        <mxCell id="external-df" value="External APIs&#xa;(Google Search, Maps)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="800" y="120" width="120" height="60" />
        </mxCell>
        
        <!-- Data Flows -->
        
        <!-- User to Frontend -->
        <mxCell id="flow-1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#82b366;startArrow=classic;startFill=1;endArrow=classic;endFill=1;" edge="1" parent="1" source="user-df" target="frontend-df">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="label-1" value="1. UI Interactions&#xa;(Travel Plans, Photos)" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#82b366;" vertex="1" connectable="0" parent="flow-1">
          <mxGeometry x="-0.1" y="2" relative="1" as="geometry">
            <mxPoint x="5" y="-15" as="offset" />
          </mxGeometry>
        </mxCell>
        
        <!-- Frontend to API -->
        <mxCell id="flow-2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;startArrow=classic;startFill=1;endArrow=classic;endFill=1;" edge="1" parent="1" source="frontend-df" target="api-df">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="label-2" value="2. REST API Calls&#xa;(JSON/FormData)" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#d6b656;" vertex="1" connectable="0" parent="flow-2">
          <mxGeometry x="-0.1" y="2" relative="1" as="geometry">
            <mxPoint x="5" y="-15" as="offset" />
          </mxGeometry>
        </mxCell>
        
        <!-- API to AI -->
        <mxCell id="flow-3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#b85450;startArrow=none;startFill=0;endArrow=classic;endFill=1;" edge="1" parent="1" source="api-df" target="ai-df">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="label-3" value="3. AI Generation&#xa;(Text + Images)" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#b85450;" vertex="1" connectable="0" parent="flow-3">
          <mxGeometry x="-0.1" y="2" relative="1" as="geometry">
            <mxPoint x="5" y="-15" as="offset" />
          </mxGeometry>
        </mxCell>
        
        <!-- API to Database -->
        <mxCell id="flow-4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;startArrow=classic;startFill=1;endArrow=classic;endFill=1;" edge="1" parent="1" source="api-df" target="db-df">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="label-4" value="4. CRUD Operations&#xa;(SQL Queries)" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#6c8ebf;" vertex="1" connectable="0" parent="flow-4">
          <mxGeometry x="-0.1" y="2" relative="1" as="geometry">
            <mxPoint x="5" y="-15" as="offset" />
          </mxGeometry>
        </mxCell>
        
        <!-- API to Cache -->
        <mxCell id="flow-5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#9673a6;startArrow=classic;startFill=1;endArrow=classic;endFill=1;" edge="1" parent="1" source="api-df" target="cache-df">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="label-5" value="5. Cache Operations&#xa;(Session, AI Results)" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#9673a6;" vertex="1" connectable="0" parent="flow-5">
          <mxGeometry x="-0.1" y="2" relative="1" as="geometry">
            <mxPoint x="5" y="-15" as="offset" />
          </mxGeometry>
        </mxCell>
        
        <!-- API to Storage -->
        <mxCell id="flow-6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d79b00;startArrow=classic;startFill=1;endArrow=classic;endFill=1;" edge="1" parent="1" source="api-df" target="storage-df">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="label-6" value="6. File Operations&#xa;(Image Upload/Download)" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#d79b00;" vertex="1" connectable="0" parent="flow-6">
          <mxGeometry x="-0.1" y="2" relative="1" as="geometry">
            <mxPoint x="5" y="-15" as="offset" />
          </mxGeometry>
        </mxCell>
        
        <!-- AI to External -->
        <mxCell id="flow-7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#666666;startArrow=none;startFill=0;endArrow=classic;endFill=1;" edge="1" parent="1" source="ai-df" target="external-df">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="label-7" value="7. Built-in Tools&#xa;(Search, Maps, Vision)" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#666666;" vertex="1" connectable="0" parent="flow-7">
          <mxGeometry x="-0.1" y="2" relative="1" as="geometry">
            <mxPoint x="5" y="-15" as="offset" />
          </mxGeometry>
        </mxCell>
        
        <!-- Data Flow Legend -->
        <mxCell id="legend" value="Data Flow Legend" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="80" y="480" width="840" height="120" />
        </mxCell>
        
        <mxCell id="legend-1" value="1. User interactions (form submissions, file uploads)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="510" width="200" height="20" />
        </mxCell>
        
        <mxCell id="legend-2" value="2. REST API communication (HTTP/HTTPS)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="320" y="510" width="200" height="20" />
        </mxCell>
        
        <mxCell id="legend-3" value="3. AI model inference (multimodal input/output)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="540" y="510" width="200" height="20" />
        </mxCell>
        
        <mxCell id="legend-4" value="4. Database operations (PostgreSQL)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="540" width="200" height="20" />
        </mxCell>
        
        <mxCell id="legend-5" value="5. Cache operations (Redis)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="320" y="540" width="200" height="20" />
        </mxCell>
        
        <mxCell id="legend-6" value="6. File storage operations (Cloud Storage)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="540" y="540" width="200" height="20" />
        </mxCell>
        
        <mxCell id="legend-7" value="7. External API calls (Google Search, Maps)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="570" width="200" height="20" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 使用方法

### Draw.ioでの読み込み手順

1. **Draw.io（diagrams.net）にアクセス**
   - https://app.diagrams.net/ を開く

2. **新規図表の作成**
   - "Create New Diagram" をクリック
   - "Blank Diagram" を選択

3. **XMLの読み込み**
   - メニューから "File" → "Import from" → "Text" を選択
   - 上記のXMLコードをコピー&ペースト
   - "Import" をクリック

4. **図表の編集**
   - 各コンポーネントの位置やスタイルを調整可能
   - 新しい要素の追加や削除も可能

### 図表の種類

1. **システム全体アーキテクチャ**: GCPサービス全体の構成
2. **ネットワーク構成図**: VPC、サブネット、セキュリティグループの詳細
3. **データフロー図**: システム間のデータの流れと処理順序

## アーキテクチャの特徴

### 正しいトラフィックフロー
- **静的コンテンツ**: Users → Firebase Hosting（Next.jsの静的ファイル）
- **API呼び出し**: Users → Load Balancer → Cloud Run（FastAPIバックエンド）
- **バックエンド処理**: Cloud Run → 各種GCPサービス（並列接続）

### 高可用性設計
- **Multi-AZ構成**: Cloud SQL の Primary/Replica 構成
- **Auto Scaling**: Cloud Run の自動スケーリング
- **Load Balancing**: Global HTTPS Load Balancer

### セキュリティ設計
- **ネットワーク分離**: Public/Private サブネット分離
- **最小権限原則**: IAM による細かい権限制御
- **暗号化**: 保存時・転送時の暗号化

### パフォーマンス最適化
- **CDN活用**: Firebase Hosting + Cloud CDN
- **キャッシュ戦略**: Redis による多層キャッシュ
- **リージョン最適化**: Asia-Northeast1 (Tokyo) 配置

### コスト最適化
- **サーバーレス**: Cloud Run による従量課金
- **ストレージ階層**: 適切なストレージクラス選択
- **リソース監視**: Cloud Monitoring による使用量監視

## 次のステップ

1. **Terraform設定の作成**
2. **CI/CDパイプラインの設計**
3. **監視・アラート設定の詳細化**
4. **セキュリティポリシーの策定**